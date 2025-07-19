import { useEffect, useState } from 'react'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import {
  AnalyzerCard,
  FeatureGrid,
  HowItWorks,
  Testimonials,
  Integrations,
  FinalCTA,
  Footer,
  type AnalyzeResponse,
} from './components'
import './index.css'

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
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between py-4">
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
        </div>
      </nav>
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
                loading={loading}
                error={error}
                result={result}
              />
            </div>
          </div>
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
