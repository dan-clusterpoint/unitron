export interface Action {
  /** Optional identifier linking to a persona */
  persona?: string
  /** Short action description */
  description: string
  /** Additional arbitrary properties */
  [key: string]: unknown
}

export interface Persona {
  /** Unique identifier */
  id: string
  /** Display name */
  name?: string
  [key: string]: unknown
}

export interface ParsedInsight {
  summary: string
  personas: Persona[]
  actions: Action[]
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
      data = { summary: payload }
    }
  }

  // drill into nested 'report' field if present
  if (data && typeof data === 'object' && 'report' in data && typeof data.report === 'object') {
    data = { ...data, ...data.report }
  }

  const summary =
    (getValue(data, ['summary', 'insight', 'report', 'text']) as string | undefined) || ''

  let personas: Persona[] = []
  const personaRaw =
    getValue(data, ['personas', 'generated_buyer_personas', 'buyer_personas']) || []
  if (Array.isArray(personaRaw)) {
    personas = personaRaw.map((p, i) => {
      if (typeof p === 'string') return { id: String(i), name: p }
      if (p && typeof p === 'object') {
        const { id = String(i), name, ...rest } = p as any
        return { id, name, ...rest }
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
  const actionRaw = getValue(data, ['actions', 'action_items', 'next_best_actions']) || []
  if (Array.isArray(actionRaw)) {
    actions = actionRaw.map((a, i) => {
      if (typeof a === 'string') return { description: a }
      if (a && typeof a === 'object') {
        const { persona, persona_id, description, action, ...rest } = a as any
        const desc = description ?? action ?? ''
        const personaRef = persona_id ?? persona
        const base: Action = { description: typeof desc === 'string' ? desc : JSON.stringify(desc) }
        if (personaRef != null) base.persona = String(personaRef)
        return { ...base, ...rest }
      }
      return { description: String(a) }
    })
  }

  return { summary, personas, actions }
}
