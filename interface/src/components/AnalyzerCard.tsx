import { useState, useEffect, useRef, type RefObject } from 'react'
import PropertyResults from './PropertyResults'
import MartechResults from './MartechResults'
import CmsResults from './CmsResults'
import InsightMarkdown from './InsightMarkdown'
import TechnologySelect from './TechnologySelect'
import { apiFetch } from '../api'
import { normalizeUrl } from '../utils'
import { requestSchema } from '../utils/requestSchema'
import { ORG_CONTEXT } from '../config/orgContext'
import { normalizeStack, type StackItem } from '../utils/tech'
import Sheet from './ui/sheet'

function hasNextBestActions(markdown: string | null) {
  return !!markdown && /^##\s*Next-Best Actions/m.test(markdown)
}

// eslint-disable-next-line react-refresh/only-export-components
export function computeMartechCount(
  martech: Record<string, string[] | Record<string, unknown>> | null,
) {
  if (!martech) return 0
  return Object.values(martech).reduce(
    (a, b) => a + (Array.isArray(b) ? b.length : Object.keys(b).length),
    0,
  )
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
  const [generating, setGenerating] = useState(false)
  const [insight, setInsight] = useState<string | null>(null)
  const [insightLoading, setInsightLoading] = useState(false)
  const [insightError, setInsightError] = useState<string | null>(null)
  const [insightMarkdown, setInsightMarkdown] = useState<string | null>(null)
  const [insightMarkdownDegraded, setInsightMarkdownDegraded] = useState(false)
  const [genError, setGenError] = useState<string | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [industry, setIndustry] = useState(() => {
    try {
      return sessionStorage.getItem('industry') || ''
    } catch {
      return ''
    }
  })
  const [painPoint, setPainPoint] = useState(() => {
    try {
      return sessionStorage.getItem('pain_point') || ''
    } catch {
      return ''
    }
  })
  const [stack, setStack] = useState<StackItem[]>(() => {
    try {
      const stored = sessionStorage.getItem('stack')
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })
  const [contextOpen, setContextOpen] = useState(false)
  const [hasGenerated, setHasGenerated] = useState(false)
  const industryRef = useRef<HTMLInputElement>(null)
  const painRef = useRef<HTMLInputElement>(null)
  const stackRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    sessionStorage.setItem('industry', industry)
  }, [industry])

  useEffect(() => {
    sessionStorage.setItem('pain_point', painPoint)
  }, [painPoint])

  useEffect(() => {
    sessionStorage.setItem('stack', JSON.stringify(stack))
    if (stack.length) {
      console.log('stack_count', stack.length)
    }
  }, [stack])

  useEffect(() => {
    if (!result) {
      setInsight(null)
      setInsightMarkdown(null)
      setGenError(null)
      setInsightError(null)
      return
    }
    const text = result.property?.notes.join('\n') || ''
    setInsightLoading(true)
    setInsightError(null)
    apiFetch<{ markdown: string; degraded: boolean }>('/insight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
      .then(async (d) => {
        const summary = d.markdown || ''
        setInsight(summary)
      })
      .catch((e) => {
        setInsightError((e as Error).message || 'Failed to fetch insight')
      })
      .finally(() => setInsightLoading(false))
  }, [result])

  async function handleGenerate() {
    setGenerating(true)
    try {
      if (!result) return
      setInsightMarkdown(null)
      setInsightMarkdownDegraded(false)
      setGenError(null)
      setValidationError(null)
      const clean = normalizeUrl(url)
      const source = (result.martech ?? {}) as {
        core?: string[]
        adjacent?: string[]
        broader?: string[]
        competitors?: string[]
      }
      const martech = {
        core: source.core ?? [],
        adjacent: source.adjacent ?? [],
        broader: source.broader ?? [],
        competitors: source.competitors ?? [],
      }
      const payload = {
        url: clean,
        martech,
        cms: result.cms || [],
        industry,
        pain_point: painPoint,
        stack: normalizeStack(stack.map((s) => s.vendor)),
        evidence_standards: ORG_CONTEXT.evidence_standards ?? '',
        credibility_scoring: ORG_CONTEXT.credibility_scoring ?? '',
        deliverable_guidelines: ORG_CONTEXT.deliverable_guidelines ?? '',
        audience: ORG_CONTEXT.audience ?? '',
        preferences: ORG_CONTEXT.preferences ?? '',
      }
      const parsed = requestSchema.safeParse(payload)
      if (!parsed.success) {
        setValidationError(parsed.error.errors.map((e) => e.message).join(', '))
        return
      }
      const data = await apiFetch<{ markdown: string; degraded: boolean }>('/insight', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      setInsightMarkdown((data.markdown ?? '').trim())
      setInsightMarkdownDegraded(data.degraded)
      setHasGenerated(true)
    } catch (e) {
      setGenError((e as Error).message)
    } finally {
      setGenerating(false)
    }
  }
  const stackCount = stack.length
  const filled = (industry ? 1 : 0) + (painPoint ? 1 : 0) + (stackCount ? 1 : 0)
  const contextStrength =
    industry && painPoint && stackCount >= 3
      ? 'High'
      : filled >= 2
        ? 'Medium'
        : 'Low'
  function focusRef(ref: RefObject<HTMLInputElement | null>) {
    setContextOpen(true)
    setTimeout(() => ref.current?.focus(), 0)
  }
  const actionsMissing = insightMarkdown !== null && !hasNextBestActions(insightMarkdown)
  const showDegradedBanner =
    insightMarkdown !== null && (insightMarkdownDegraded || actionsMissing)
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
            <CmsResults cms={cms} />
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
        <>
          {hasGenerated && (
            <div className="mt-4">
              <div className="flex flex-wrap gap-2">
                {industry && (
                  <button
                    className="border rounded-full px-2 py-0.5 text-xs"
                    onClick={() => focusRef(industryRef)}
                  >
                    {industry}
                  </button>
                )}
                {painPoint && (
                  <button
                    className="border rounded-full px-2 py-0.5 text-xs"
                    onClick={() => focusRef(painRef)}
                  >
                    {painPoint}
                  </button>
                )}
                {stackCount > 0 && (
                  <button
                    className="border rounded-full px-2 py-0.5 text-xs"
                    onClick={() => focusRef(stackRef)}
                  >
                    {`Stack (${stackCount})`}
                  </button>
                )}
              </div>
              <div className="text-xs text-gray-600 mt-1">
                Context strength: {contextStrength}
              </div>
            </div>
          )}
          <button
            className="btn-primary mt-4"
            disabled={generating || insightLoading}
            onClick={handleGenerate}
          >
            {generating ? 'Generating...' : 'Generate Insights'}
          </button>
          {(generating || insightMarkdown !== null) && (
            <section className="bg-gray-50 p-4 rounded mt-4">
              {showDegradedBanner && (
                <div className="border border-amber-500 bg-amber-50 text-amber-700 p-2 rounded mb-4 text-sm">
                  Partial results—model returned limited content.{' '}
                  <button
                    className="underline"
                    onClick={() => setContextOpen(true)}
                  >
                    Improve results: add tools to Stack, set Industry, describe a Pain point.
                  </button>
                </div>
              )}
              <InsightMarkdown
                markdown={insightMarkdown ?? ''}
                loading={generating}
              />
            </section>
          )}
          <Sheet open={contextOpen} onClose={() => setContextOpen(false)}>
            <h2 className="font-medium mb-4">Context</h2>
            <div className="space-y-2">
              <input
                aria-label="Industry"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="Industry"
                className="border rounded p-2 w-full"
                ref={industryRef}
              />
              <input
                aria-label="Pain point"
                value={painPoint}
                onChange={(e) => setPainPoint(e.target.value)}
                placeholder="Pain point"
                className="border rounded p-2 w-full"
                ref={painRef}
              />
              <TechnologySelect
                value={stack}
                onChange={setStack}
                inputRef={stackRef}
              />
            </div>
          </Sheet>
          {validationError && (
            <div className="border border-red-500 text-red-600 p-2 rounded mt-4 text-sm">
              {validationError}
            </div>
          )}
          {genError && (
            <div className="border border-red-500 text-red-600 p-2 rounded mt-4 text-sm">
              {genError}
            </div>
          )}
        </>
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
