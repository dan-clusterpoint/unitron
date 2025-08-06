import { render, screen } from '@testing-library/react'

// dynamic import to respect env flag before evaluation

test('hides legacy Domains heading when flag enabled', async () => {
  const old = import.meta.env.VITE_USE_JIT_DOMAINS
  import.meta.env.VITE_USE_JIT_DOMAINS = 'true'
  const { default: PropertyResults } = await import('./components/PropertyResults')
  render(<PropertyResults property={{ confidence: 0.9 }} />)
  expect(screen.queryByRole('heading', { name: /Domains/i })).not.toBeInTheDocument()
  import.meta.env.VITE_USE_JIT_DOMAINS = old
})
