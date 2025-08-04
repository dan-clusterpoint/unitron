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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const payload: Snapshot = {
          profile: {
            name: 'Acme Inc',
            industry: 'SaaS',
            location: 'NYC',
            website: 'https://acme.com',
          },
          digitalScore: 80,
          riskMatrix: { x: 1, y: 2 } as any,
          stackDelta: [{ label: 'React', status: 'added' }],
          growthTriggers: ['Improve SEO'],
          nextActions: [{ label: 'Analyze stack', targetId: 'stack' }],
        }
        const data = await apiFetch<{ snapshot: Snapshot }>(
          '/snapshot',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          },
        )
        setSnapshot(data.snapshot)
      } catch {
        setError('Failed to load analysis')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [])

  if (loading) return <div className="p-4">Loading...</div>
  if (error) return <div className="p-4 text-red-600">{error}</div>
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
