import { useEffect, useState } from 'react'
import { useFadeInOnView, useScrollPosition } from './hooks'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import { apiFetch, BASE_URL } from './api'
import { normalizeUrl } from './utils'
import ScopeChip from './components/domain/ScopeChip'
import { USE_JIT_DOMAINS } from './config'
import {
  AnalyzerCard,
  FeatureGrid,
  HowItWorks,
  Testimonials,
  Integrations,
  FinalCTA,
  Footer,
} from './components'
import ExecutiveSummaryCard, {
  type ExecutiveSummaryCardProps,
} from './components/summary/ExecutiveSummaryCard'
import './index.css'

type Snapshot = {
  profile: ExecutiveSummaryCardProps['profile']
  digitalScore: number
  riskMatrix: ExecutiveSummaryCardProps['risk']
  stackDelta: ExecutiveSummaryCardProps['stack']
  growthTriggers: string[]
  nextActions: ExecutiveSummaryCardProps['actions']
}

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [health, setHealth] = useState<'green' | 'yellow' | 'red'>('red')
  const [menuOpen, setMenuOpen] = useState(false)
  const [banner, setBanner] = useState('')
  const [headless, setHeadless] = useState(false)
  const [force, setForce] = useState(false)
  const { showTop } = useScrollPosition()
  useFadeInOnView()

  async function checkHealth() {
    try {
      const data = await apiFetch<{ ready: boolean }>('/ready')
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
    if (!BASE_URL) {
      setBanner('API base URL not configured \u2013 update your .env file')
    }
  }, [])


  async function onAnalyze() {
    setError('')
    setSnapshot(null)
    setLoading(true)
    try {
      const clean = normalizeUrl(url)
      const payload: Snapshot = {
        profile: { name: clean },
        digitalScore: 0,
        riskMatrix: { x: 0, y: 0 },
        stackDelta: [],
        growthTriggers: [],
        nextActions: [],
      }
      const data = await apiFetch<{ snapshot: Snapshot }>(
        '/snapshot',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        },
      )
      setSnapshot(data.snapshot)
    } catch (err) {
      setError('Failed to analyze. Please try again.')
      if (err instanceof Error && err.message) {
        setBanner(err.message)
      } else {
        setBanner('Network error. Please retry.')
      }
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
      <header className="sticky top-0 z-[1000] bg-white p-4 md:px-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="font-bold text-xl">Unitron</div>
        </div>
        <nav className="hidden md:flex items-center text-sm">
          {USE_JIT_DOMAINS && <ScopeChip onRerun={onAnalyze} />}
          <a href="#home" className="mx-3 font-semibold text-dark hover:text-accent">Home</a>
          <a href="/docs" className="mx-3 font-semibold text-dark hover:text-accent">Docs</a>
          <a href="https://github.com" className="mx-3 font-semibold text-dark hover:text-accent" target="_blank" rel="noreferrer">GitHub</a>
          <a href="#contact" className="mx-3 font-semibold text-dark hover:text-accent">Contact</a>
          <button
            aria-label="scroll to form"
            onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
            className="btn-primary"
          >
            Analyze Now
          </button>
        </nav>
        <div className="md:hidden flex items-center space-x-4">
          <span
            className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${
              health === 'green'
                ? 'bg-green-100 text-green-800'
                : health === 'yellow'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {health === 'green' ? 'Ready' : health === 'yellow' ? 'Degraded' : 'Down'}
          </span>
          <button aria-label="open menu" onClick={() => setMenuOpen(true)}>
            <Bars3Icon className="w-5 h-5" />
          </button>
        </div>
      </header>
      {menuOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-20 flex justify-end md:hidden">
          <div className="bg-white w-2/3 max-w-xs p-4 space-y-4">
            <button className="mb-4" aria-label="close menu" onClick={() => setMenuOpen(false)}>
              <XMarkIcon className="w-5 h-5" />
            </button>
            <a href="#home" className="block py-1" onClick={() => setMenuOpen(false)}>Home</a>
            <a href="/docs" className="block py-1" onClick={() => setMenuOpen(false)}>Docs</a>
            <a href="https://github.com" className="block py-1" target="_blank" rel="noreferrer" onClick={() => setMenuOpen(false)}>GitHub</a>
            <a href="#contact" className="block py-1" onClick={() => setMenuOpen(false)}>Contact</a>
          </div>
        </div>
      )}
      <main className="pt-20" id="home">
        {snapshot ? (
          <div className="max-w-6xl mx-auto px-4 py-16">
            <ExecutiveSummaryCard
              profile={snapshot.profile}
              score={snapshot.digitalScore}
              risk={snapshot.riskMatrix}
              stack={snapshot.stackDelta}
              triggers={
                snapshot.growthTriggers.length > 0
                  ? snapshot.growthTriggers
                  : ['—']
              }
              actions={snapshot.nextActions}
            />
          </div>
        ) : (
          <>
            <section className="bg-white" data-observe>
              <div className="max-w-6xl mx-auto px-4 py-16">
                <div className="text-center space-y-6">
                  <div>
                    <h1 className="text-4xl font-extrabold mb-4">Unitron: AI-First Workflow Analyzer</h1>
                    <p className="text-lg text-neutral leading-relaxed">
                      Reverse-engineer any domain and surface next-best actions.
                    </p>
                  </div>
                  <AnalyzerCard
                    id="analyzer"
                    url={url}
                    setUrl={setUrl}
                    onAnalyze={onAnalyze}
                    headless={headless}
                    setHeadless={setHeadless}
                    force={force}
                    setForce={setForce}
                    loading={loading}
                    error={error}
                    result={null}
                  />
                </div>
              </div>
            </section>
            <FeatureGrid />
            <HowItWorks />
            <Testimonials />
            <Integrations />
            <FinalCTA />
          </>
        )}
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
