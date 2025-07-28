import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '../setupTests'
import { http } from 'msw'
import { test, expect, vi } from 'vitest'
import type { AnalyzeResult } from './AnalyzerCard'
import { computeMartechCount } from './AnalyzerCard'

test('shows spinner when loading', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  const { container } = render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={true}
      error=""
      result={null}
    />,
  )
  expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
})

test('displays error message', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error="oops"
      result={null}
    />,
  )
  expect(screen.getByText('oops')).toBeInTheDocument()
})

const result: AnalyzeResult = {
  property: {
    domains: ['example.com'],
    confidence: 1,
    notes: ['note'],
  },
  martech: {
    core: ['GTM'],
  },
  degraded: false,
}

test('renders result lists', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={result}
    />,
  )
  expect(screen.getByText('example.com')).toBeInTheDocument()
  expect(screen.getByText('GTM')).toBeInTheDocument()
})

test('shows degraded banner', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={{ ...result, degraded: true }}
    />,
  )
  expect(screen.getByText(/partial results/i)).toBeInTheDocument()
})

test('shows CMS placeholder when array empty', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={{ ...result, cms: [] }}
    />,
  )
  const cmsSection = screen.getByRole('heading', {
    name: 'Content Management Systems',
  }).parentElement as HTMLElement
  expect(within(cmsSection).getByText('Nothing detected')).toBeInTheDocument()
  expect(within(cmsSection).getByLabelText('CMS')).toBeInTheDocument()
})

test('displays insight text', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={{ ...result, cms: [] }}
    />,
  )
  await screen.findByText('Test insight')
  const btn = screen.getByRole('button', { name: /generate insights/i })
  expect(btn).toBeEnabled()
})

test('shows generated details on success', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/generate', async ({ request }) => {
      const body = await request.json()
      expect(body).toEqual({ url: 'https://example.com', cms: [] })
      return Response.json({ result: { personas: ['P1'], demo_flow: 'Flow' } })
    }),
  )
  render(
    <AnalyzerCard
      id="a"
      url="example.com"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={{ ...result, cms: [] }}
    />,
  )
  await screen.findByText('Test insight')
  const btn = screen.getByRole('button', { name: /generate insights/i })
  await userEvent.click(btn)
  await screen.findByText('P1')
  screen.getByText('Flow')
})

test('shows error when generation fails', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(http.post('/generate', () => new Response(null, { status: 500 })))
  render(
    <AnalyzerCard
      id="a"
      url="example.com"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={{ ...result, cms: [] }}
    />,
  )
  await screen.findByText('Test insight')
  const btn = screen.getByRole('button', { name: /generate insights/i })
  await userEvent.click(btn)
  await screen.findByText('HTTP 500')
})

test('shows insight error and button enabled on insight failure', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(http.post('/insight', () => new Response(null, { status: 500 })))
  render(
    <AnalyzerCard
      id="a"
      url="example.com"
      setUrl={() => {}}
      onAnalyze={() => {}}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={{ ...result, cms: [] }}
    />,
  )
  await screen.findByText('HTTP 500')
  const btn = screen.getByRole('button', { name: /generate insights/i })
  expect(btn).toBeEnabled()
})

test('counts nested martech buckets correctly', () => {
  const nested: AnalyzeResult = {
    property: { domains: [], confidence: 0.5, notes: [] },
    martech: { core: ['A'], adjacent: { one: {}, two: {} } },
    degraded: false,
  }
  expect(computeMartechCount(nested.martech)).toBe(3)
})
