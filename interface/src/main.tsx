// Build-time sanity check for API base URL
console.log(
  '🛠 BUILD VITE_API_BASE_URL →',
  import.meta.env.VITE_API_BASE_URL,
)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
