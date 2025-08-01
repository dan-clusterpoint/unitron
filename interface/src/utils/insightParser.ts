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

  if (insight.evidence && typeof insight.evidence === 'object') {
    const ev = insight.evidence as any
    const ins = ev.insights
    if (ins == null) ev.insights = []
    else if (!Array.isArray(ins)) ev.insights = [ins]
  }

  let actionRaw = insight.actions ?? []
  let evidenceRaw = insight.evidence ?? ''
  const personaRaw = (data as any)?.personas ?? []
  let extraPersonaRaw: unknown = null

  const actionEmpty =
    (Array.isArray(actionRaw) && actionRaw.length === 0) ||
    (actionRaw && typeof actionRaw === 'object' && !Array.isArray(actionRaw) && Object.keys(actionRaw).length === 0)
  if (
    actionEmpty &&
    evidenceRaw &&
    typeof evidenceRaw === 'object' &&
    'NextBestAction' in (evidenceRaw as any)
  ) {
    const evObj = evidenceRaw as any
    extraPersonaRaw = evObj.Persona
    actionRaw = [evObj.NextBestAction]
    evidenceRaw = evObj.evidence ?? ''
  }

  let evidence = ''
  if (typeof evidenceRaw === 'string') evidence = evidenceRaw
  else if (evidenceRaw != null) evidence = JSON.stringify(evidenceRaw)

  let personas: Persona[] = []
  if (Array.isArray(personaRaw)) {
    personas = personaRaw.map((p, i) => {
      if (typeof p === 'string')
        return { id: String(i), name: p, demographics: 'unknown', needs: 'unknown', goals: 'unknown' }
      if (p && typeof p === 'object') {
        const {
          id = String(i),
          name = '',
          demographics = 'unknown',
          needs = 'unknown',
          goals = 'unknown',
          ...rest
        } = p as any
        return { id: String(id), name, demographics, needs, goals, ...rest }
      }
      return {
        id: String(i),
        name: String(p),
        demographics: 'unknown',
        needs: 'unknown',
        goals: 'unknown',
      }
    })
  } else if (personaRaw && typeof personaRaw === 'object') {
    personas = Object.entries(personaRaw).map(([k, v]) => {
      if (typeof v === 'string')
        return { id: k, name: v, demographics: 'unknown', needs: 'unknown', goals: 'unknown' }
      if (v && typeof v === 'object') {
        const {
          name = '',
          demographics = 'unknown',
          needs = 'unknown',
          goals = 'unknown',
          ...rest
        } = v as any
        return { id: k, name, demographics, needs, goals, ...rest }
      }
      return {
        id: k,
        name: String(v),
        demographics: 'unknown',
        needs: 'unknown',
        goals: 'unknown',
      }
    })
  }

  if (extraPersonaRaw != null) {
    const i = personas.length
    const p = extraPersonaRaw as any
    if (typeof p === 'string')
      personas.push({
        id: String(i),
        name: p,
        demographics: 'unknown',
        needs: 'unknown',
        goals: 'unknown',
      })
    else if (p && typeof p === 'object') {
      const {
        id = String(i),
        name = '',
        demographics = 'unknown',
        needs = 'unknown',
        goals = 'unknown',
        ...rest
      } = p as any
      personas.push({ id: String(id), name, demographics, needs, goals, ...rest })
    } else {
      personas.push({
        id: String(i),
        name: String(p),
        demographics: 'unknown',
        needs: 'unknown',
        goals: 'unknown',
      })
    }
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
