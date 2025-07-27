import { useState, useEffect } from 'react'
import PropertyResults from './PropertyResults'
import MartechResults from './MartechResults'
import CmsResults from './CmsResults'
import { apiFetch } from '../api'
import { normalizeUrl } from '../utils'

export type AnalyzeResult = {
  property: {
    domains: string[]
    confidence: number
    notes: string[]
  } | null
  martech: Record<string, string[]> | null
  cms?: string[] | null
  degraded: boolean
}

export type AnalyzerProps = {
  id: string
  url: string
  setUrl: (v: string) => void
  onAnalyze: () => void
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
  const [manualCms, setManualCms] = useState('')
  const [generating, setGenerating] = useState(false)
  const [insight, setInsight] = useState<string | null>(null)
  const [insightLoading, setInsightLoading] = useState(false)

  useEffect(() => {
    if (!result) {
      setInsight(null)
      return
    }
    const text = result.property?.notes.join('\n') || ''
    setInsightLoading(true)
    apiFetch<{ result: { insight?: string } }>('/insight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
      .then((d) => setInsight(d.result.insight || ''))
      .catch(() => setInsight(''))
      .finally(() => setInsightLoading(false))
  }, [result])

  async function onGenerate() {
    if (!result) return
    setGenerating(true)
    try {
      const clean = normalizeUrl(url)
      await apiFetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: clean,
          martech: result.martech || {},
          cms: result.cms || [],
          ...(manualCms ? { cms_manual: manualCms } : {}),
        }),
      })
    } finally {
      setGenerating(false)
    }
  }
  if (result) {
    const { property, martech, cms, degraded } = result
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow prose">
        <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
        {degraded && (
          <div className="border border-yellow-500 bg-yellow-50 text-yellow-700 p-2 rounded mb-4 text-sm">
            Partial results shown due to degraded analysis.
          </div>
        )}
        {property && <PropertyResults property={property} />}
        {martech && <MartechResults martech={martech} />}
        {cms != null && (
          <CmsResults
            cms={cms}
            manualCms={manualCms}
            setManualCms={setManualCms}
          />
        )}
        {(insightLoading || insight) && (
          <div className="bg-gray-50 p-4 rounded mb-4">
            <h3 className="font-medium mb-2">Insights</h3>
            {insightLoading ? <p>Loading...</p> : <p>{insight || 'None'}</p>}
          </div>
        )}
        {cms && cms.length === 0 && (
          <button
            className="btn-primary mt-4"
            disabled={generating || insightLoading || !insight}
            onClick={onGenerate}
          >
            {generating ? 'Generating...' : 'Generate Insights'}
          </button>
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
          onClick={onAnalyze}
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
