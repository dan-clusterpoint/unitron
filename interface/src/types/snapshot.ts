import type { ExecutiveSummaryCardProps } from '../components/summary'

export interface Snapshot {
  profile: ExecutiveSummaryCardProps['profile']
  digitalScore: number
  vendors: ExecutiveSummaryCardProps['vendors']
  growthTriggers: string[]
}

