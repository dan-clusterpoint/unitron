// Build-time sanity check for API base URL
console.log(
  '🛠 BUILD VITE_API_BASE_URL →',
  import.meta.env.VITE_API_BASE_URL,
)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import AnalysisResultPage from './pages/AnalysisResultPage'
import { ErrorBoundary } from './components'
import { DomainProvider } from './contexts/DomainContext'

const RootComponent =
  window.location.pathname === '/analysis' ? AnalysisResultPage : App

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <DomainProvider>
      <ErrorBoundary>
        <RootComponent />
      </ErrorBoundary>
    </DomainProvider>
  </StrictMode>,
)
