export type AnalyzeResult = {
  property: {
    domains: string[]
    confidence: number
    notes: string[]
  } | null
  martech: Record<string, string[]> | null
  degraded: boolean
}

export type AnalyzerProps = {
  id: string
  url: string
  setUrl: (v: string) => void
  onAnalyze: () => void
  loading: boolean
  error: string
  result: AnalyzeResult | null
}

function renderList(items?: string[]) {
  if (!items || items.length === 0) return <p className="italic">Nothing detected</p>
  return (
    <ul className="list-disc list-inside space-y-1">
      {items.map((i) => (
        <li key={i}>{i}</li>
      ))}
    </ul>
  )
}

export default function AnalyzerCard({ id, url, setUrl, onAnalyze, loading, error, result }: AnalyzerProps) {
  if (result) {
    const { property, martech } = result
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow prose">
        <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
        {property && (
          <>
            <div className="bg-gray-50 p-4 rounded mb-4">
              <h3 className="font-medium">Domains</h3>
              {renderList(property.domains)}
            </div>
            <div className="bg-gray-50 p-4 rounded mb-4">
              <h3 className="font-medium">Confidence</h3>
              <p>{property.confidence}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded mb-4">
              <h3 className="font-medium mb-2">Notes</h3>
              {renderList(property.notes)}
            </div>
          </>
        )}
        {martech && (
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-medium mb-2">Martech Vendors</h3>
            {Object.keys(martech).length === 0 ? (
              <p className="italic">Nothing detected</p>
            ) : (
              Object.entries(martech).map(([bucket, vendors]) => (
                <div key={bucket} className="mb-2">
                  <h4 className="font-medium capitalize">{bucket}</h4>
                  {renderList(vendors)}
                </div>
              ))
            )}
          </div>
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
    </div>
  )
}
