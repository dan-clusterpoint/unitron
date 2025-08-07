import type { ExecutiveSummaryCardProps } from '../components/summary'

export interface Snapshot {
  profile: ExecutiveSummaryCardProps['profile']
  digitalScore: number
  stack: ExecutiveSummaryCardProps['stack']
  growthTriggers: string[]
}

