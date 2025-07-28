import { useState, useEffect } from 'react'
import PropertyResults from './PropertyResults'
import MartechResults from './MartechResults'
import CmsResults from './CmsResults'
import { apiFetch } from '../api'
import { normalizeUrl, downloadBase64 } from '../utils'

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
  downloads?: Record<string, string>
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
  const [insightError, setInsightError] = useState<string | null>(null)
  const [downloads, setDownloads] = useState<Record<string, string> | null>(null)
  const [generated, setGenerated] = useState<{ personas: string[]; demo_flow: string } | null>(
    null,
  )
  const [genError, setGenError] = useState<string | null>(null)

  useEffect(() => {
    if (!result) {
      setInsight(null)
      setDownloads(null)
      setGenerated(null)
      setGenError(null)
      setInsightError(null)
      return
    }
    const text = result.property?.notes.join('\n') || ''
    setInsightLoading(true)
    setInsightError(null)
    apiFetch<{ result: { insight?: string } }>('/insight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
      .then(async (d) => {
        const summary = d.result.insight || ''
        setInsight(summary)
        try {
          const post = await apiFetch<{ downloads?: Record<string, string> }>('/postprocess-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ report: { summary } }),
          })
          setDownloads(post.downloads || null)
        } catch {
          setDownloads(null)
        }
      })
      .catch((e) => {
        setInsightError((e as Error).message || 'Failed to fetch insight')
        setDownloads(null)
      })
      .finally(() => setInsightLoading(false))
  }, [result])

  async function onGenerate() {
    if (!result) return
    setGenerating(true)
    setGenerated(null)
    setGenError(null)
    try {
      const clean = normalizeUrl(url)
      const data = await apiFetch<{ result: { personas: string[]; demo_flow: string } }>('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: clean,
          cms: result.cms || [],
          ...(manualCms ? { cms_manual: manualCms } : {}),
        }),
      })
      setGenerated(data.result)
    } catch (e) {
      setGenError((e as Error).message)
    } finally {
      setGenerating(false)
    }
  }
  if (result) {
    const { property, martech, cms, degraded } = result
    const domainCount = property?.domains.length || 0
    const martechCount = computeMartechCount(martech)
    const cmsCount = cms?.length || 0
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow prose">
        <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
        <nav aria-label="Sections" className="mb-4">
          <ul className="flex flex-wrap gap-2 text-sm">
            <li>
              <a href="#exec-summary" className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500" tabIndex={0}>Summary</a>
            </li>
            {property && (
              <li>
                <a href="#property" className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500" tabIndex={0}>Property</a>
              </li>
            )}
            {martech && (
              <li>
                <a href="#martech" className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500" tabIndex={0}>Martech</a>
              </li>
            )}
            {cms != null && (
              <li>
                <a href="#cms" className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500" tabIndex={0}>CMS</a>
              </li>
            )}
            {property && property.notes.length > 0 && (
              <li>
                <a href="#footnotes" className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500" tabIndex={0}>Footnotes</a>
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
            <div className="text-lg font-semibold">{Math.round((property?.confidence || 0) * 100)}%</div>
            <div className="text-xs">Confidence</div>
          </div>
          <div className="p-3 rounded bg-gray-800 text-white text-center">
            <div className="text-lg font-semibold">{martechCount}</div>
            <div className="text-xs">Martech Vendors</div>
          </div>
          <div className="p-3 rounded bg-gray-800 text-white text-center">
            <div className="text-lg font-semibold">{cmsCount}</div>
            <div className="text-xs">CMS</div>
          </div>
        </div>
        {degraded && (
          <div className="border border-yellow-500 bg-yellow-50 text-yellow-700 p-2 rounded mb-4 text-sm">
            Partial results shown due to degraded analysis.
          </div>
        )}
        {(insightLoading || insight || insightError) && (
          <>
            <section id="exec-summary" className="bg-gray-50 p-4 rounded mb-2">
              <h3 className="font-medium mb-2">Executive Summary</h3>
              {insightLoading ? <p>Loading...</p> : <p>{insight || 'None'}</p>}
              {downloads && (
                <div className="mt-2 flex gap-2">
                  {downloads.markdown && (
                    <button
                      className="btn-primary text-sm"
                      onClick={() => downloadBase64(downloads.markdown as string, 'report.md')}
                    >
                      Download Markdown
                    </button>
                  )}
                  {downloads.scenarios && (
                    <button
                      className="btn-primary text-sm"
                      onClick={() => downloadBase64(downloads.scenarios as string, 'scenarios.csv')}
                    >
                      Download CSV
                    </button>
                  )}
                </div>
              )}
            </section>
            {insightError && (
              <div className="border border-red-500 text-red-600 p-2 rounded mb-4 text-sm">
                {insightError}
              </div>
            )}
          </>
        )}
        {property && <section id="property"><PropertyResults property={property} /></section>}
        {martech && <section id="martech"><MartechResults martech={martech} /></section>}
        {cms != null && (
          <section id="cms">
            <CmsResults cms={cms} manualCms={manualCms} setManualCms={setManualCms} />
          </section>
        )}
        {property && property.notes.length > 0 && (
          <section id="footnotes" className="bg-gray-50 p-4 rounded mt-4">
            <h3 className="font-medium mb-2">Footnotes</h3>
            <ol className="list-decimal list-inside space-y-1">
              {property.notes.map((n, i) => (
                <li key={i} id={`fn${i + 1}`}>{n} <a href={`#fnref${i + 1}`} className="underline text-blue-800 ml-1" tabIndex={0}>↩</a></li>
              ))}
            </ol>
          </section>
        )}
        {cms && cms.length === 0 && (
          <>
            <button
              className="btn-primary mt-4"
              disabled={generating || insightLoading}
              onClick={onGenerate}
            >
              {generating ? 'Generating...' : 'Generate Insights'}
            </button>
            {generated && (
              <section className="bg-gray-50 p-4 rounded mt-4">
                <h3 className="font-medium mb-2">Demo Flow</h3>
                <p>{generated.demo_flow}</p>
                <h4 className="font-medium mt-2">Personas</h4>
                <ul className="list-disc list-inside">
                  {generated.personas.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </section>
            )}
            {genError && (
              <div className="border border-red-500 text-red-600 p-2 rounded mt-4 text-sm">
                {genError}
              </div>
            )}
          </>
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
