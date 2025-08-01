import { render, screen, within, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '../setupTests'
import { http } from 'msw'
import { test, expect, vi } from 'vitest'
import type { AnalyzeResult } from './AnalyzerCard'
import { computeMartechCount } from './AnalyzerCard'
import { ORG_CONTEXT } from '../config/orgContext'

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
  const btn = await screen.findByRole('button', { name: /generate insights/i })
  expect(btn).toBeEnabled()
})

test('shows skeleton while generating', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () => {
      await new Promise((r) => setTimeout(r, 50))
      return Response.json({ markdown: 'done', degraded: false })
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
  const btn = await screen.findByRole('button', { name: /generate insights/i })
  await waitFor(() => expect(btn).toBeEnabled())
  await userEvent.click(btn)
  await screen.findByTestId('insight-skeleton')
})

test('shows generated details on success', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async ({ request }) => {
      const body = await request.json()
      expect(body).toEqual({
        url: 'https://example.com',
        martech: {
          core: (result.martech as any)?.core ?? [],
          adjacent: (result.martech as any)?.adjacent ?? [],
          broader: (result.martech as any)?.broader ?? [],
          competitors: (result.martech as any)?.competitors ?? [],
        },
        cms: [],
        evidence_standards: ORG_CONTEXT.evidence_standards ?? '',
        credibility_scoring: ORG_CONTEXT.credibility_scoring ?? '',
        deliverable_guidelines: ORG_CONTEXT.deliverable_guidelines ?? '',
        audience: ORG_CONTEXT.audience ?? '',
        preferences: ORG_CONTEXT.preferences ?? '',
      })
      return Response.json({ markdown: 'Flow', degraded: false })
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
  const btn = await screen.findByRole('button', { name: /generate insights/i })
  await waitFor(() => expect(btn).toBeEnabled())
  await userEvent.click(btn)
  await screen.findByText('Flow')
})

test('shows fallback when markdown empty', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () => Response.json({ markdown: '', degraded: false })),
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
  const btn = await screen.findByRole('button', { name: /generate insights/i })
  await waitFor(() => expect(btn).toBeEnabled())
  await userEvent.click(btn)
  await screen.findByText('Analysis unavailable')
})

test('shows error when generation fails', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', () => new Response(null, { status: 500 }))
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
  const btn = await screen.findByRole('button', { name: /generate insights/i })
  await waitFor(() => expect(btn).toBeEnabled())
  await userEvent.click(btn)
  const errs = await screen.findAllByText('HTTP 500')
  expect(errs.length).toBeGreaterThan(0)
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

test('shows validation error and skips POST on invalid payload', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  const spy = vi.fn()
  server.use(
    http.post('/insight', async ({ request }) => {
      const body = await request.json()
      if (!('text' in body)) spy()
      return Response.json({})
    }),
  )
  const badResult: AnalyzeResult = {
    property: { domains: ['example.com'], confidence: 1, notes: ['note'] },
    martech: { core: [1 as any] },
    degraded: false,
  }
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
      result={{ ...badResult, cms: [] }}
    />,
  )
  const btn = await screen.findByRole('button', { name: /generate insights/i })
  await waitFor(() => expect(btn).toBeEnabled())
  await userEvent.click(btn)
  await screen.findByText(/Expected string/i)
  expect(spy).not.toHaveBeenCalled()
})
