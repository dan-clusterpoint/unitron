import { useEffect, useState } from 'react'
import './index.css'

type AnalyzeResponse = {
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

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [health, setHealth] = useState<'green' | 'yellow' | 'red'>('red')

  async function checkHealth() {
    try {
      const res = await fetch('/ready')
      if (!res.ok) throw new Error('status ' + res.status)
      const data = await res.json()
      setHealth(data.ready ? 'green' : 'yellow')
    } catch {
      setHealth('red')
    }
  }

  useEffect(() => {
    checkHealth()
    const id = setInterval(checkHealth, 30000)
    return () => clearInterval(id)
  }, [])

  async function onAnalyze() {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      if (!res.ok) throw new Error(`${res.status}`)
      const data: AnalyzeResponse = await res.json()
      setResult(data)
    } catch (err) {
      setError('Failed to analyze. Please try again.')
    } finally {
      setLoading(false)
    }
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

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-4">
      <header className="w-full flex justify-between items-center mb-8">
        <h1 className="text-xl font-semibold">Unitron Analyzer</h1>
        <span
          className={`px-2 py-1 rounded text-sm font-medium ${
            health === 'green'
              ? 'bg-green-600'
              : health === 'yellow'
              ? 'bg-yellow-500'
              : 'bg-red-600'
          }`}
        >
          {health === 'green' ? 'Ready' : health === 'yellow' ? 'Degraded' : 'Down'}
        </span>
      </header>
      <div className="w-full max-w-md space-y-4">
        {error && <div className="bg-red-800 text-red-100 p-2 rounded">{error}</div>}
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          className="w-full p-2 rounded bg-gray-800 border border-gray-700"
        />
        <button
          onClick={onAnalyze}
          disabled={loading || !url}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 p-2 rounded"
        >
          {loading ? <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : 'Analyze'}
        </button>
        {result && (
          <div className="bg-gray-800 p-4 rounded shadow space-y-4">
            <div>
              <h2 className="font-semibold text-lg mb-2">Properties</h2>
              <p>Domain: {result.domain}</p>
              <p>Confidence: {result.confidence ?? 'N/A'}</p>
              <p>Notes: {result.notes || <span className="italic">None</span>}</p>
            </div>
            <div>
              <h2 className="font-semibold text-lg mb-2">Martech</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium">Core</h3>
                  {renderList(result.martech?.core)}
                </div>
                <div>
                  <h3 className="font-medium">Adjacent</h3>
                  {renderList(result.martech?.adjacent)}
                </div>
                <div>
                  <h3 className="font-medium">Broader</h3>
                  {renderList(result.martech?.broader)}
                </div>
                <div>
                  <h3 className="font-medium">Competitors</h3>
                  {renderList(result.martech?.competitors)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
