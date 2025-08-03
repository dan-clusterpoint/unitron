import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import { server } from './setupTests'
import { http } from 'msw'
import App from './App'
import { type AnalyzeResult } from './components'

beforeEach(() => {
  global.IntersectionObserver = vi.fn(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
  })) as unknown as typeof IntersectionObserver
})

test('shows loading spinner and displays result', async () => {
  const full: AnalyzeResult = {
    property: {
      domains: ['example.com'],
      confidence: 1,
      notes: [],
    },
    martech: { core: ['GTM'] },
    degraded: false,
  }
  server.use(
    http.post('/analyze', async ({ request }) => {
      const body = await request.json()
      expect(body).toEqual({ url: 'https://example.com', headless: false, force: false })
      await new Promise((r) => setTimeout(r, 1000))
      return Response.json(full)
    })
  )
  render(<App />)
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'example.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await waitFor(() =>
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument(),
  )
  await screen.findByText(/example\.com/i, undefined, { timeout: 2000 })
  await screen.findByDisplayValue('GTM')
})

test('shows error banner when request fails', async () => {
  server.use(
    http.post('/analyze', async ({ request }) => {
      const body = await request.json()
      expect(body).toEqual({ url: 'https://example.com', headless: false, force: false })
      return new Response(null, { status: 500 })
    })
  )
  render(<App />)
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'example.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await screen.findByText('Failed to analyze. Please try again.')
  screen.getByText('HTTP 500')
  await userEvent.click(screen.getByRole('button', { name: /dismiss/i }))
  await waitFor(() =>
    expect(screen.queryByText('HTTP 500')).not.toBeInTheDocument(),
  )
})

test('shows degraded banner when martech is null', async () => {
  const partial: AnalyzeResult = {
    property: {
      domains: ['partial.com'],
      confidence: 0.5,
      notes: [],
    },
    martech: null,
    degraded: true,
  }
  server.use(
    http.post('/analyze', async ({ request }) => {
      const body = await request.json()
      expect(body).toEqual({ url: 'https://partial.com', headless: false, force: false })
      return Response.json(partial)
    })
  )
  render(<App />)
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'partial.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await screen.findByText('partial.com')
  await screen.findByText(/partial results/i)
})
