export type AnalyzeResponse = {
  domain: string
  confidence?: number
  notes?: string
  martech?: {
    core?: string[]
    adjacent?: string[]
    broader?: string[]
    competitors?: string[]
  }
}

export type AnalyzerProps = {
  id: string
  url: string
  setUrl: (v: string) => void
  onAnalyze: () => void
  loading: boolean
  error: string
  result: AnalyzeResponse | null
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
    const empty =
      !result.martech?.core?.length &&
      !result.martech?.adjacent?.length &&
      !result.martech?.broader?.length &&
      !result.martech?.competitors?.length
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow prose">
        <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
        {empty ? (
          <p>We couldn’t find any insights for that domain.</p>
        ) : (
          <>
            <div className="bg-gray-50 p-4 rounded mb-4">
              <h3 className="font-medium">Properties</h3>
              <p>Domain: {result.domain}</p>
              <p>Confidence: {result.confidence ?? 'N/A'}</p>
              <p>Notes: {result.notes || <span className="italic">None</span>}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <h3 className="font-medium mb-2">Martech</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium">Core</h4>
                  {renderList(result.martech?.core)}
                </div>
                <div>
                  <h4 className="font-medium">Adjacent</h4>
                  {renderList(result.martech?.adjacent)}
                </div>
                <div>
                  <h4 className="font-medium">Broader</h4>
                  {renderList(result.martech?.broader)}
                </div>
                <div>
                  <h4 className="font-medium">Competitors</h4>
                  {renderList(result.martech?.competitors)}
                </div>
              </div>
            </div>
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
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://example.com"
        aria-label="URL to analyze"
        className="w-full p-2 rounded border border-gray-300 mb-4"
      />
      <button
        aria-label="analyze"
        onClick={onAnalyze}
        disabled={loading || !url}
        className="w-full bg-primary hover:bg-primary-dark disabled:opacity-50 text-white py-2 rounded transition active:scale-95"
      >
        {loading ? (
          <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
        ) : (
          'Analyze'
        )}
      </button>
    </div>
  )
}
