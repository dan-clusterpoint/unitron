import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, test, expect, beforeEach } from 'vitest'
import { server } from './setupTests'
import { http } from 'msw'
import App from './App'
import { DomainProvider } from './contexts/DomainContext'

beforeEach(() => {
  global.IntersectionObserver = vi.fn(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
  })) as unknown as typeof IntersectionObserver
})

test('renders executive summary when snapshot returned', async () => {
  const snapshot = {
    profile: { name: 'Acme Inc.' },
    digitalScore: 88,
    stackDelta: [],
    growthTriggers: ['Trigger'],
    nextActions: [],
  }
  server.use(
    http.post('/snapshot', async () => {
      return Response.json({ snapshot })
    }),
  )
  render(
    <DomainProvider>
      <App />
    </DomainProvider>,
  )
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'example.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await screen.findByText('Acme Inc.')
  expect(
    screen.queryByRole('button', { name: /analyze/i }),
  ).not.toBeInTheDocument()
})

test('shows error banner when request fails', async () => {
  server.use(
    http.post('/snapshot', () => new Response(null, { status: 500 })),
  )
  render(
    <DomainProvider>
      <App />
    </DomainProvider>,
  )
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'example.com')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await screen.findByText('Failed to analyze. Please try again.')
  screen.getByText('HTTP 500')
  await userEvent.click(screen.getByRole('button', { name: /dismiss/i }))
  await screen.findByRole('button', { name: /analyze/i })
})

