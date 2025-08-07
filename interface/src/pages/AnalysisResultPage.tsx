import { useEffect, useState } from 'react'
import ExecutiveSummaryCard from '../components/summary/ExecutiveSummaryCard'
import { apiFetch } from '../api'
import type { Snapshot } from '../types/snapshot'

export default function AnalysisResultPage() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)

  useEffect(() => {
    async function load() {
      const url = window.location.href
      const data = await apiFetch<{ snapshot: Snapshot }>('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      setSnapshot(data.snapshot)
    }
    void load()
  }, [])

  if (!snapshot) return null
  return (
    <div className="p-4">
      <ExecutiveSummaryCard
        profile={snapshot.profile}
        score={snapshot.digitalScore}
        vendors={snapshot.vendors}
        triggers={snapshot.growthTriggers}
      />
    </div>
  )
}
