import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import { server } from './setupTests'
import { http } from 'msw'
import App from './App'

beforeEach(() => {
  global.IntersectionObserver = vi.fn(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
  })) as unknown as typeof IntersectionObserver
})

test('shows loading spinner and displays result', async () => {
  server.use(
    http.post('/analyze', async () => {
      await new Promise((r) => setTimeout(r, 1000))
      return Response.json({
        property: {
          domains: ['example.com'],
          confidence: 1,
          notes: [],
        },
        martech: { core: ['GTM'] },
        degraded: false,
      })
    })
  )
  render(<App />)
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'https://example.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await waitFor(() =>
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument(),
  )
  await screen.findByText('example.com')
  await screen.findByText('GTM')
})

test('shows error banner when request fails', async () => {
  server.use(http.post('/analyze', () => new Response(null, { status: 500 })))
  render(<App />)
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'https://example.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await screen.findByText('Failed to analyze. Please try again.')
  screen.getByText('HTTP 500')
  await userEvent.click(screen.getByRole('button', { name: /dismiss/i }))
  await waitFor(() =>
    expect(screen.queryByText('HTTP 500')).not.toBeInTheDocument(),
  )
})
