import type { ExecutiveSummaryCardProps } from '../components/summary'

export interface Snapshot {
  profile: ExecutiveSummaryCardProps['profile']
  digitalScore: number
  risk?: ExecutiveSummaryCardProps['risk']
  riskMatrix?: ExecutiveSummaryCardProps['risk']
  stackDelta: ExecutiveSummaryCardProps['stack']
  growthTriggers: string[]
  nextActions: ExecutiveSummaryCardProps['actions']
}

