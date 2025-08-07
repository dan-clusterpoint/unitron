import { useState, useEffect } from 'react'
import PropertyResults from './PropertyResults'
import MartechCategorySelector, {
  type MartechItem,
} from './MartechCategorySelector'
import {
  ExecutiveSummaryCard,
  type ExecutiveSummaryCardProps,
} from './summary'
import catalog from '../data/martech_catalog.json'
import type { Snapshot } from '../types/snapshot'

const vendorToCategory: Record<string, string> = {}
for (const [cat, info] of Object.entries(catalog)) {
  if (cat === '_comment') continue
  ;(info as { vendors: string[] }).vendors.forEach((v) => {
    vendorToCategory[v] = cat
  })
}

// eslint-disable-next-line react-refresh/only-export-components
export function computeMartechCount(
  martech: Record<string, string[] | Record<string, unknown>> | null,
) {
  return martech
    ? Object.values(martech).reduce(
        (a, b) => a + (Array.isArray(b) ? b.length : Object.keys(b).length),
        0,
      )
    : 0
}

export type AnalyzeResult = {
  property: {
    domains: string[]
    confidence: number
    notes: string[]
  } | null
  martech: Record<string, string[] | Record<string, unknown>> | null
  cms?: string[] | null
  degraded: boolean
}

export type { Snapshot } from '../types/snapshot'

export type AnalyzerProps = {
  id: string
  url: string
  setUrl: (v: string) => void
  onAnalyze: () => Promise<Snapshot | null>
  headless: boolean
  setHeadless: (v: boolean) => void
  force: boolean
  setForce: (v: boolean) => void
  loading: boolean
  error: string
  result: AnalyzeResult | null
}


export default function AnalyzerCard({
  id,
  url,
  setUrl,
  onAnalyze,
  headless,
  setHeadless,
  force,
  setForce,
  loading,
  error,
  result,
}: AnalyzerProps) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [martechManual, setMartechManual] = useState<MartechItem[]>([])

  async function handleAnalyze() {
    const snap = await onAnalyze()
    setSnapshot(snap)
  }

  useEffect(() => {
    if (result?.martech) {
      const all = new Set<string>()
      for (const list of Object.values(result.martech)) {
        if (Array.isArray(list)) {
          for (const v of list) {
            all.add(v)
          }
        }
      }
      const arr: MartechItem[] = []
      for (const v of all) {
        const cat = vendorToCategory[v]
        if (cat) {
          arr.push({ category: cat, vendor: v })
        }
      }
      setMartechManual(arr)
    }
  }, [result])

  if (result) {
    const { property, martech, degraded } = result
    const domainCount = property?.domains.length || 0
    const martechCount = computeMartechCount(martech)
    const snapshotForCard: ExecutiveSummaryCardProps | null = snapshot
      ? {
          profile: snapshot.profile,
          score: snapshot.digitalScore,
          risk: snapshot.risk,
          stack: snapshot.stackDelta,
          triggers: snapshot.growthTriggers,
          actions: snapshot.nextActions,
        }
      : null
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow prose">
        <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
        <nav aria-label="Sections" className="mb-4">
          <ul className="flex flex-wrap gap-2 text-sm">
            {property && (
              <li>
                <a
                  href="#property"
                  className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500"
                  tabIndex={0}
                >
                  Property
                </a>
              </li>
            )}
            {martech && (
              <li>
                <a
                  href="#martech"
                  className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500"
                  tabIndex={0}
                >
                  Martech
                </a>
              </li>
            )}
          </ul>
        </nav>
        <div className="grid grid-cols-2 gap-4 mb-4" role="region" aria-label="Key metrics">
          <div className="p-3 rounded bg-gray-800 text-white text-center">
            <div className="text-lg font-semibold">{domainCount}</div>
            <div className="text-xs">Domains</div>
          </div>
          <div className="p-3 rounded bg-gray-800 text-white text-center">
            <div className="text-lg font-semibold">
              {Math.round((property?.confidence || 0) * 100)}%
            </div>
            <div className="text-xs">Confidence</div>
          </div>
          <div className="p-3 rounded bg-gray-800 text-white text-center">
            <div className="text-lg font-semibold">{martechCount}</div>
            <div className="text-xs">Martech Vendors</div>
          </div>
        </div>
        {degraded && (
          <div className="border border-yellow-500 bg-yellow-50 text-yellow-700 p-2 rounded mb-4 text-sm">
            Partial results shown due to degraded analysis.
          </div>
        )}
        {snapshotForCard && (
          <div className="mb-4">
            <ExecutiveSummaryCard {...snapshotForCard} />
          </div>
        )}
        {property && (
          <section id="property">
            <PropertyResults property={property} />
          </section>
        )}
        {martech && (
          <section id="martech">
            <MartechCategorySelector
              value={martechManual}
              onChange={setMartechManual}
            />
          </section>
        )}
      </div>
    )
  }
  if (loading) {
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
    )
  }
  return (
    <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow">
      {error && <div className="border border-red-500 text-red-600 p-2 rounded mb-4 text-sm">{error}</div>}
      <div className="hero-form">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          aria-label="URL to analyze"
          className="flex-1 py-3 px-4 border border-gray-300 rounded-l-md placeholder-gray-500 focus:border-[var(--accent-orange)] focus:shadow-[0_0_0_3px_rgba(251,146,137,.2)] focus:outline-none"
        />
        <button
          aria-label="analyze"
          onClick={() => void handleAnalyze()}
          disabled={loading || !url}
          className="btn-primary rounded-l-none rounded-r-md h-full min-w-[8rem] disabled:opacity-50 active:scale-95"
        >
          {loading ? (
            <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
          ) : (
            'Analyze'
          )}
        </button>
      </div>
      <label className="flex items-center mt-4 text-sm">
        <input
          type="checkbox"
          checked={headless}
          onChange={(e) => setHeadless(e.target.checked)}
          className="mr-2"
        />
        Enable deep scan
      </label>
      <label className="flex items-center mt-2 text-sm">
        <input
          type="checkbox"
          checked={force}
          onChange={(e) => setForce(e.target.checked)}
          className="mr-2"
        />
        Force refresh
      </label>
    </div>
  )
}
