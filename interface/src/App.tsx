import { useEffect, useState } from 'react'
import {
  HeartIcon,
  ChartBarIcon,
  HomeIcon,
  RocketLaunchIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
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
  const [menuOpen, setMenuOpen] = useState(false)
  const [banner, setBanner] = useState('')
  const [showTop, setShowTop] = useState(false)

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
    const onScroll = () => {
      setScrolled(window.scrollY > 10)
      setShowTop(window.scrollY > 200)
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.classList.add('fade-in')
      })
    }, { threshold: 0.1 })
    document.querySelectorAll('[data-observe]').forEach((el) => observer.observe(el))
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
      setBanner('Network error. Please retry.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {banner && (
        <div className="bg-red-500 text-white text-center py-2 text-sm flex justify-between px-4">
          <span>{banner}</span>
          <button aria-label="dismiss" onClick={() => setBanner('')}>
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      )}
      <nav
        className={`fixed w-full z-10 transition-colors duration-300 ${scrolled ? 'bg-white shadow' : 'bg-transparent'}`}
      >
        <div className="container flex items-center justify-between py-4">
          <div className="font-bold text-xl">Unitron</div>
          <div className="hidden md:flex items-center space-x-6 text-sm">
            <a href="#home" className="hover:text-primary">Home</a>
            <a href="/docs" className="hover:text-primary">Docs</a>
            <a href="https://github.com" className="hover:text-primary" target="_blank" rel="noreferrer">GitHub</a>
            <a href="#contact" className="hover:text-primary">Contact</a>
            <button
              aria-label="scroll to form"
              onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
              className="ml-4 px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition"
            >
              Analyze Now
            </button>
          </div>
          <div className="md:hidden flex items-center space-x-4">
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                health === 'green'
                  ? 'bg-green-600 text-white'
                  : health === 'yellow'
                  ? 'bg-yellow-500 text-white'
                  : 'bg-red-600 text-white'
              }`}
            >
              {health === 'green' ? 'Ready' : health === 'yellow' ? 'Degraded' : 'Down'}
            </span>
            <button aria-label="open menu" onClick={() => setMenuOpen(true)}>
              <Bars3Icon className="w-6 h-6" />
            </button>
          </div>
        </div>
      </nav>
      {menuOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-20 flex justify-end md:hidden">
          <div className="bg-white w-2/3 max-w-xs p-4 space-y-4">
            <button className="mb-4" aria-label="close menu" onClick={() => setMenuOpen(false)}>
              <XMarkIcon className="w-6 h-6" />
            </button>
            <a href="#home" className="block py-1" onClick={() => setMenuOpen(false)}>Home</a>
            <a href="/docs" className="block py-1" onClick={() => setMenuOpen(false)}>Docs</a>
            <a href="https://github.com" className="block py-1" target="_blank" rel="noreferrer" onClick={() => setMenuOpen(false)}>GitHub</a>
            <a href="#contact" className="block py-1" onClick={() => setMenuOpen(false)}>Contact</a>
          </div>
        </div>
      )}
      <main className="pt-20" id="home">
        <section className="py-16 bg-white" data-observe>
          <div className="container max-w-4xl grid gap-8 lg:grid-cols-2 items-center">
            <div>
              <h1 className="text-4xl font-extrabold mb-4">Unitron: AI-First Workflow Analyzer</h1>
              <p className="text-lg text-neutral mb-6 leading-relaxed">Reverse-engineer any domain and surface next-best actions.</p>
            </div>
            <div className="flex justify-center">
              <img src="/vite.svg" alt="Illustration" className="w-64 h-64" />
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
      {showTop && (
        <button
          aria-label="back to top"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="fixed bottom-4 right-4 bg-primary text-white p-3 rounded-full shadow-md hover:bg-primary-dark transition"
        >
          ↑
        </button>
      )}
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

function FeatureGrid() {
  const features = [
    { title: 'Healthchecks', desc: 'Automated readiness and liveness probes', icon: <HeartIcon className="w-8 h-8 text-primary" /> },
    { title: 'Property Analysis', desc: 'Reverse-engineer key site details', icon: <HomeIcon className="w-8 h-8 text-primary" /> },
    { title: 'Martech Analysis', desc: 'Detect marketing technologies in use', icon: <ChartBarIcon className="w-8 h-8 text-primary" /> },
    { title: 'Pipeline Runner', desc: 'Automate data flows end-to-end', icon: <RocketLaunchIcon className="w-8 h-8 text-primary" /> },
  ]
  return (
    <section className="py-12 bg-gray-50" data-observe>
      <div className="container grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((f) => (
          <div key={f.title} className="bg-white p-6 rounded-lg shadow text-center space-y-2">
            <div className="flex justify-center">{f.icon}</div>
            <h3 className="font-semibold text-lg">{f.title}</h3>
            <p className="text-sm text-neutral leading-relaxed">{f.desc}</p>
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
    <section className="py-12" data-observe>
      <div className="container">
        <h2 className="text-2xl font-bold text-center mb-8">How It Works</h2>
        <div className="flex flex-col md:flex-row md:justify-center md:space-x-12 space-y-6 md:space-y-0">
          {steps.map((s, i) => (
            <div key={i} className="flex items-start md:flex-col md:items-center text-center">
              <span className="w-8 h-8 flex items-center justify-center rounded-full bg-primary text-white font-semibold">
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
    <section className="py-12 bg-gray-50" data-observe>
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
    <section className="py-8" data-observe>
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
    <section className="py-12 bg-dark text-white text-center" data-observe>
      <h2 className="text-3xl font-bold mb-4">Start Analyzing Today</h2>
      <button
        onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
        className="bg-primary hover:bg-primary-dark px-6 py-3 rounded transition"
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
              aria-label="email"
              className="flex-1 p-2 rounded text-gray-900"
            />
            <button type="submit" className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition">
              Sign Up
            </button>
          </form>
        </div>
      </div>
      <div className="text-center text-sm py-4 border-t border-gray-700">
        © {new Date().getFullYear()} Unitron · Developed with ❤️ by Unitron
      </div>
    </footer>
  )
}
