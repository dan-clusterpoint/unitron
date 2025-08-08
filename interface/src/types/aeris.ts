export interface AerisBreakdownItem {
  name: string
  score: number
}

export interface AerisPeerItem {
  name: string
  score: number
}

export interface AerisVariantItem {
  name: string
  score: number
}

export interface AerisResponse {
  core_score: number
  signal_breakdown?: AerisBreakdownItem[]
  peers?: AerisPeerItem[]
  variants?: AerisVariantItem[]
  opportunities?: string[]
  narratives?: string[]
  degraded: boolean
}
