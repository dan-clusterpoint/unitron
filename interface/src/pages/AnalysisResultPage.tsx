import { useEffect, useState } from 'react'
import ExecutiveSummaryCard, { type ExecutiveSummaryCardProps } from '../components/summary/ExecutiveSummaryCard'
import { apiFetch } from '../api'

type Snapshot = {
  profile: ExecutiveSummaryCardProps['profile']
  digitalScore: number
  riskMatrix?: ExecutiveSummaryCardProps['risk']
  stackDelta: ExecutiveSummaryCardProps['stack']
  growthTriggers: string[]
  nextActions: ExecutiveSummaryCardProps['actions']
}

export default function AnalysisResultPage() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)

  useEffect(() => {
    async function load() {
      const data = await apiFetch<{ snapshot: Snapshot }>('/analyze')
      setSnapshot(data.snapshot)
    }
    void load()
  }, [])

  if (!snapshot) return null

  const triggers =
    snapshot.growthTriggers.length > 0 ? snapshot.growthTriggers : ['—']

  return (
    <div className="p-4">
      <ExecutiveSummaryCard
        profile={snapshot.profile}
        score={snapshot.digitalScore}
        risk={snapshot.riskMatrix}
        stack={snapshot.stackDelta}
        triggers={triggers}
        actions={snapshot.nextActions}
      />
    </div>
  )
}
