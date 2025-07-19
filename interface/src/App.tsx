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

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [health, setHealth] = useState<'green' | 'yellow' | 'red'>('red')
  const [scrolled, setScrolled] = useState(false)

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

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  async function onAnalyze() {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
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

  return (
    <>
      <nav
        className={`fixed w-full z-10 transition-colors duration-300 ${scrolled ? 'bg-white shadow' : 'bg-transparent'}`}
      >
        <div className="container flex items-center justify-between py-4">
          <div className="font-bold text-xl">Unitron</div>
          <div className="hidden md:flex items-center space-x-6 text-sm">
            <a href="#home" className="hover:text-brand">Home</a>
            <a href="/docs" className="hover:text-brand">Docs</a>
            <a href="https://github.com" className="hover:text-brand" target="_blank" rel="noreferrer">GitHub</a>
            <a href="#contact" className="hover:text-brand">Contact</a>
            <button
              aria-label="open-form"
              onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
              className="ml-4 px-4 py-2 bg-brand text-white rounded hover:bg-brand-dark"
            >
              Analyze Now
            </button>
          </div>
          <span
            className={`md:hidden px-2 py-1 rounded text-xs font-medium ${
              health === 'green'
                ? 'bg-green-600 text-white'
                : health === 'yellow'
                ? 'bg-yellow-500 text-white'
                : 'bg-red-600 text-white'
            }`}
          >
            {health === 'green' ? 'Ready' : health === 'yellow' ? 'Degraded' : 'Down'}
          </span>
        </div>
      </nav>
      <main className="pt-20" id="home">
        <section className="py-16 bg-white">
          <div className="container max-w-4xl grid gap-8 lg:grid-cols-2 items-center">
            <div>
              <h1 className="text-4xl font-extrabold mb-4">Unitron: AI-First Workflow Analyzer</h1>
              <p className="text-lg text-gray-600 mb-6">Reverse-engineer any domain and surface next-best actions.</p>
            </div>
            <div className="flex justify-center">
              <img src="/vite.svg" alt="Hero" className="w-64 h-64" />
            </div>
          </div>
          <AnalyzerCard
            id="analyzer"
            url={url}
            setUrl={setUrl}
            onAnalyze={onAnalyze}
            loading={loading}
            error={error}
            result={result}
          />
        </section>
        <FeatureGrid />
        <HowItWorks />
        <Testimonials />
        <Integrations />
        <FinalCTA />
      </main>
      <Footer />
    </>
  )
}

type AnalyzerProps = {
  id: string
  url: string
  setUrl: (v: string) => void
  onAnalyze: () => void
  loading: boolean
  error: string
  result: AnalyzeResponse | null
}

function AnalyzerCard({ id, url, setUrl, onAnalyze, loading, error, result }: AnalyzerProps) {
  if (result) {
    return (
      <div id={id} className="max-w-lg mx-auto my-12 p-6 bg-white rounded-lg shadow prose">
        <h2 className="text-xl font-semibold mb-4">Analysis Result</h2>
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
        className="w-full p-2 rounded border border-gray-300 mb-4"
      />
      <button
        onClick={onAnalyze}
        disabled={loading || !url}
        className="w-full bg-brand hover:bg-brand-dark disabled:opacity-50 text-white py-2 rounded"
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

function FeatureGrid() {
  const features = [
    { title: 'Healthchecks', desc: 'Automated readiness and liveness probes', icon: '❤️' },
    { title: 'Property Analysis', desc: 'Reverse-engineer key site details', icon: '🏠' },
    { title: 'Martech Analysis', desc: 'Detect marketing technologies in use', icon: '📊' },
    { title: 'Pipeline Runner', desc: 'Automate data flows end-to-end', icon: '🚀' },
  ]
  return (
    <section className="py-12 bg-gray-50">
      <div className="container grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((f) => (
          <div key={f.title} className="bg-white p-6 rounded-lg shadow text-center space-y-2">
            <div className="text-3xl">{f.icon}</div>
            <h3 className="font-semibold">{f.title}</h3>
            <p className="text-sm text-gray-600">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function HowItWorks() {
  const steps = [
    'Enter a URL',
    'Unitron analyzes core, adjacent, broader vendors',
    'View results inline',
  ]
  return (
    <section className="py-12">
      <div className="container">
        <h2 className="text-2xl font-bold text-center mb-8">How It Works</h2>
        <div className="flex flex-col md:flex-row md:justify-center md:space-x-12 space-y-6 md:space-y-0">
          {steps.map((s, i) => (
            <div key={i} className="flex items-start md:flex-col md:items-center text-center">
              <span className="w-8 h-8 flex items-center justify-center rounded-full bg-brand text-white font-semibold">
                {i + 1}
              </span>
              <span className="ml-3 md:ml-0 md:mt-3 text-sm font-medium">{s}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Testimonials() {
  const items = [
    { name: 'Alex', quote: 'Unitron saved us hours of analysis.' },
    { name: 'Jamie', quote: 'Incredibly easy to integrate into our workflow.' },
    { name: 'Taylor', quote: 'A must-have tool for presales teams.' },
  ]
  return (
    <section className="py-12 bg-gray-50">
      <div className="container flex overflow-x-auto space-x-6">
        {items.map((t) => (
          <div key={t.name} className="flex-none w-80 bg-white p-6 rounded-lg shadow">
            <div className="flex items-center space-x-4 mb-2">
              <div className="w-10 h-10 rounded-full bg-gray-200" />
              <div className="font-medium">{t.name}</div>
            </div>
            <p className="text-sm text-gray-600">“{t.quote}”</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function Integrations() {
  const items = ['S3', 'Postgres', 'n8n', 'Redis']
  return (
    <section className="py-8">
      <div className="container flex flex-wrap justify-center items-center space-x-4">
        {items.map((i) => (
          <span key={i} className="px-4 py-2 bg-gray-100 rounded text-sm font-medium">
            {i}
          </span>
        ))}
      </div>
    </section>
  )
}

function FinalCTA() {
  return (
    <section className="py-12 bg-dark text-white text-center">
      <h2 className="text-3xl font-bold mb-4">Start Analyzing Today</h2>
      <button
        onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
        className="bg-brand hover:bg-brand-dark px-6 py-3 rounded"
      >
        Get Started
      </button>
    </section>
  )
}

function Footer() {
  return (
    <footer className="bg-gray-800 text-gray-300" id="contact">
      <div className="container py-12 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
        <div>
          <h3 className="font-semibold mb-2">Site</h3>
          <ul className="space-y-1 text-sm">
            <li><a href="#home" className="hover:text-white">Home</a></li>
            <li><a href="/docs" className="hover:text-white">Docs</a></li>
            <li><a href="https://github.com" className="hover:text-white">GitHub</a></li>
            <li><a href="#contact" className="hover:text-white">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="font-semibold mb-2">Newsletter</h3>
          <form className="flex space-x-2">
            <input
              type="email"
              placeholder="Your email"
              className="flex-1 p-2 rounded text-gray-900"
            />
            <button type="submit" className="px-4 py-2 bg-brand text-white rounded">
              Sign Up
            </button>
          </form>
        </div>
      </div>
      <div className="text-center text-sm py-4 border-t border-gray-700">
        © {new Date().getFullYear()} Unitron
      </div>
    </footer>
  )
}
