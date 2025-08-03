import { render, screen } from '@testing-library/react'
import { DomainProvider } from './contexts/DomainContext'
import { vi } from 'vitest'

// dynamic import inside test to apply env flag before module evaluation

test('renders scope chip when flag enabled', async () => {
  const old = import.meta.env.VITE_USE_JIT_DOMAINS
  import.meta.env.VITE_USE_JIT_DOMAINS = 'true'
  global.IntersectionObserver = vi.fn(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
  })) as unknown as typeof IntersectionObserver
  const { default: App } = await import('./App')
  render(
    <DomainProvider>
      <App />
    </DomainProvider>,
  )
  await screen.findByRole('button', { name: /Domains/ })
  import.meta.env.VITE_USE_JIT_DOMAINS = old
})
