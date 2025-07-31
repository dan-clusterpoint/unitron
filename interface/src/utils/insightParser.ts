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

function getValue(obj: any, keys: string[]): any {
  for (const k of keys) {
    if (obj && typeof obj === 'object' && k in obj) {
      return (obj as any)[k]
    }
  }
  return undefined
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
      data = { evidence: payload }
    }
  }

  // drill into nested 'report' field if present
  if (data && typeof data === 'object' && 'report' in data && typeof data.report === 'object') {
    data = { ...data, ...data.report }
  }


  // flatten nested 'result' field if present
  if (data && typeof data === 'object' && 'result' in data && typeof (data as any).result === 'object') {
    data = { ...data, ...(data as any).result }
  }

  // flatten nested 'insight' field
  if (data && typeof data === 'object' && 'insight' in data && typeof data.insight === 'object') {
    const { insight, ...rest } = data as any
    data = { ...rest, ...insight }
  }

  const evidenceRaw = getValue(data, ['evidence', 'summary', 'insight', 'report', 'text'])
  let evidence = ''
  if (typeof evidenceRaw === 'string') {
    evidence = evidenceRaw
  } else if (evidenceRaw && typeof evidenceRaw === 'object') {
    const nested = getValue(evidenceRaw, [
      'evidence',
      'summary',
      'insight',
      'report',
      'text',
    ])
    if (typeof nested === 'string') evidence = nested
    else if (nested === undefined) evidence = ''
    else evidence = JSON.stringify(evidenceRaw)
  } else if (evidenceRaw != null) {
    evidence = String(evidenceRaw)
  }

  let personas: Persona[] = []
  const personaRaw = getValue(data, ['personas', 'generated_buyer_personas', 'buyer_personas']) || []
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
  const nested =
    data &&
    typeof data === 'object' &&
    (data as any).result &&
    typeof (data as any).result === 'object' &&
    (data as any).result.insight &&
    typeof (data as any).result.insight === 'object' &&
    Array.isArray((data as any).result.insight.insights)
      ? (data as any).result.insight.insights
      : undefined

  let actionRaw =
    getValue(data, ['actions', 'action_items', 'next_best_actions']) || []

  if (
    (!actionRaw ||
      (Array.isArray(actionRaw) && actionRaw.length === 0)) &&
    Array.isArray((data as any).insights)
  ) {
    actionRaw = (data as any).insights
  }

  if (
    (!actionRaw ||
      (Array.isArray(actionRaw) && actionRaw.length === 0)) &&
    Array.isArray(nested)
  ) {
    actionRaw = nested
  }

  if (Array.isArray(actionRaw)) {
    actions = actionRaw.map((item, idx) => {
      if (typeof item === 'string') {
        return { id: String(idx + 1), title: item, reasoning: '', benefit: '' }
      }
      if (item && typeof item === 'object') {
        const {
          name,
          description,
          title = '',
          reasoning = '',
          benefit = '',
          action,
          ...rest
        } = item as any
        const titleVal = name || title || action || 'Action'
        const reasonVal = description || reasoning || ''
        return {
          id: String(idx + 1),
          title: titleVal,
          reasoning: reasonVal,
          benefit,
          ...rest,
        }
      }
      return { id: String(idx + 1), title: String(item), reasoning: '', benefit: '' }
    })
  } else if (actionRaw && typeof actionRaw === 'object') {
    actions = Object.entries(actionRaw).map(([k, v]) => {
      if (typeof v === 'string') {
        return { id: k, title: v, reasoning: '', benefit: '' }
      }
      if (v && typeof v === 'object') {
        const {
          name,
          description,
          title = '',
          reasoning = '',
          benefit = '',
          action,
          ...rest
        } = v as any
        const titleVal = name || title || action || 'Action'
        const reasonVal = description || reasoning || ''
        return { id: k, title: titleVal, reasoning: reasonVal, benefit, ...rest }
      }
      return { id: k, title: String(v), reasoning: '', benefit: '' }
    })
  }

  const degradedRaw = getValue(data, ['degraded'])
  const degraded = Boolean(degradedRaw)

  return { actions, evidence, personas, degraded }
}
