export interface Action {
  id: string
  title: string
  reasoning: string
  benefit: string
  [key: string]: unknown
}

export interface Persona {
  id: string
  name?: string
  demographics?: string
  needs?: string
  goals?: string
  [key: string]: unknown
}

export interface ParsedInsight {
  actions: Action[]
  evidence: string
  personas: Persona[]
  degraded: boolean
}

/**
 * Parse various insight payload shapes returned by the backend.
 * Strings are interpreted as JSON when possible.
 */
export function parseInsightPayload(payload: unknown): ParsedInsight {
  let data: any = payload
  if (typeof payload === 'string') {
    try {
      data = JSON.parse(payload)
    } catch {
      data = { insight: { evidence: payload } }
    }
  }

  if (data && typeof data === 'object' && 'result' in data && typeof (data as any).result === 'object') {
    data = (data as any).result
  }

  const insight = (data as any)?.insight ?? {}

  const actionRaw = insight.actions ?? []
  const evidenceRaw = insight.evidence ?? ''
  const personaRaw = (data as any)?.personas ?? []

  let evidence = ''
  if (typeof evidenceRaw === 'string') evidence = evidenceRaw
  else if (evidenceRaw != null) evidence = JSON.stringify(evidenceRaw)

  let personas: Persona[] = []
  if (Array.isArray(personaRaw)) {
    personas = personaRaw.map((p, i) => {
      if (typeof p === 'string') return { id: String(i), name: p }
      if (p && typeof p === 'object') {
        const { id = String(i), name = '', demographics, needs, goals, ...rest } = p as any
        return { id: String(id), name, demographics, needs, goals, ...rest }
      }
      return { id: String(i), name: String(p) }
    })
  } else if (personaRaw && typeof personaRaw === 'object') {
    personas = Object.entries(personaRaw).map(([k, v]) => {
      if (typeof v === 'string') return { id: k, name: v }
      if (v && typeof v === 'object') return { id: k, ...(v as any) }
      return { id: k, name: String(v) }
    })
  }

  let actions: Action[] = []
  if (Array.isArray(actionRaw)) {
    actions = actionRaw.map((item, idx) => {
      if (typeof item === 'string') {
        return { id: String(idx + 1), title: item, reasoning: '', benefit: '' }
      }
      if (item && typeof item === 'object') {
        const { id = String(idx + 1), title, name, reasoning, description, benefit = '', action, ...rest } = item as any
        const titleVal = title ?? name ?? action ?? 'Action'
        const reasonVal = reasoning ?? description ?? ''
        return { id: String(id), title: titleVal, reasoning: reasonVal, benefit, ...rest }
      }
      return { id: String(idx + 1), title: String(item), reasoning: '', benefit: '' }
    })
  } else if (actionRaw && typeof actionRaw === 'object') {
    actions = Object.entries(actionRaw).map(([k, v]) => {
      if (typeof v === 'string') return { id: k, title: v, reasoning: '', benefit: '' }
      if (v && typeof v === 'object') {
        const { title, name, reasoning, description, benefit = '', action, ...rest } = v as any
        const titleVal = title ?? name ?? action ?? 'Action'
        const reasonVal = reasoning ?? description ?? ''
        return { id: k, title: titleVal, reasoning: reasonVal, benefit, ...rest }
      }
      return { id: k, title: String(v), reasoning: '', benefit: '' }
    })
  }

  const degraded = Boolean((data as any)?.degraded)

  return { actions, evidence, personas, degraded }
}
