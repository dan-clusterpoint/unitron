/* eslint-disable @typescript-eslint/no-explicit-any */
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '../setupTests'
import { http } from 'msw'
import { test, expect, vi } from 'vitest'
import type { AnalyzeResult } from './AnalyzerCard'
import { computeMartechCount } from './AnalyzerCard'
import { ORG_CONTEXT } from '../config/orgContext'
import { INSIGHT_SKELETON_MIN_HEIGHT } from './InsightMarkdown'

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
  expect(
    screen.getByRole('heading', { name: 'Confidence' })
  ).toBeInTheDocument()
  expect(
    screen.getByRole('tab', { name: /Content Management System/i })
  ).toBeInTheDocument()
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
  const skeleton = await screen.findByTestId('insight-skeleton')
  const container = skeleton.firstElementChild as HTMLElement
  expect(container.style.minHeight).toBe(
    `${INSIGHT_SKELETON_MIN_HEIGHT}px`,
  )
})

test('keeps skeleton height during delayed insight response', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () => {
      await new Promise((r) => setTimeout(r, 100))
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
  const skeleton = await screen.findByTestId('insight-skeleton')
  const container = skeleton.firstElementChild as HTMLElement
  const initialHeight = container.style.minHeight
  await new Promise((r) => setTimeout(r, 50))
  expect(screen.getByTestId('insight-skeleton')).toBeInTheDocument()
  expect(container.style.minHeight).toBe(initialHeight)
})

test('shows generated details on success', async () => {
  sessionStorage.setItem('industry', 'SaaS')
  sessionStorage.setItem('pain_point', 'Slow onboarding')

  let captured: any = null
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async ({ request }) => {
      captured = await request.json()
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
  await waitFor(() => expect(screen.getAllByText('Flow').length).toBeGreaterThan(0))
  expect(screen.queryByTestId('insight-skeleton')).toBeNull()
  expect(captured).toEqual({
    url: 'https://example.com',
    martech: {
      core: (result.martech as any)?.core ?? [],
      adjacent: (result.martech as any)?.adjacent ?? [],
      broader: (result.martech as any)?.broader ?? [],
      competitors: (result.martech as any)?.competitors ?? [],
    },
    cms: [],
    industry: 'SaaS',
    pain_point: 'Slow onboarding',
    evidence_standards: ORG_CONTEXT.evidence_standards ?? '',
    credibility_scoring: ORG_CONTEXT.credibility_scoring ?? '',
    deliverable_guidelines: ORG_CONTEXT.deliverable_guidelines ?? '',
    audience: ORG_CONTEXT.audience ?? '',
    preferences: ORG_CONTEXT.preferences ?? '',
  })
  sessionStorage.clear()
})

test('hides skeleton on error', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () => {
      await new Promise((r) => setTimeout(r, 50))
      return new Response('fail', { status: 500 })
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
  await screen.findByText('fail')
  await waitFor(() =>
    expect(screen.queryByTestId('insight-skeleton')).toBeNull(),
  )
})

test('renders empty markdown without fallback', async () => {
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
  await waitFor(() =>
    expect(screen.queryByText('Analysis unavailable')).toBeNull(),
  )
})

test('shows banner when insight degraded', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () =>
      Response.json({
        markdown: '## Next-Best Actions\n- A',
        degraded: true,
      }),
    ),
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
  await screen.findByText('Partial results—model returned limited content.')
})

test('shows banner when actions missing', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () =>
      Response.json({ markdown: '# Hi', degraded: false }),
    ),
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
  await screen.findByText('Partial results—model returned limited content.')
})

test('nudge opens context panel and keeps content', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () =>
      Response.json({ markdown: 'Hi', degraded: false }),
    ),
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
  const nudge = await screen.findByText(
    'Improve results: set Industry, describe a Pain point.',
  )
  await userEvent.click(nudge)
  await screen.findByLabelText('Industry')
  expect(screen.getAllByText('Hi').length).toBeGreaterThan(0)
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
      if (
        body &&
        typeof body === 'object' &&
        !Array.isArray(body) &&
        !('text' in body)
      )
        spy()
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

test('chips reflect live values', async () => {
  sessionStorage.setItem('industry', 'SaaS')
  sessionStorage.setItem('pain_point', 'Latency')
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () =>
      Response.json({ markdown: 'Hi', degraded: false }),
    ),
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
  await screen.findByText('SaaS')
  await screen.findByText('Latency')
  const industryChip = screen.getByText('SaaS')
  await userEvent.click(industryChip)
  const industryInput = await screen.findByLabelText('Industry')
  await userEvent.clear(industryInput)
  await userEvent.type(industryInput, 'Commerce')
  await waitFor(() => expect(screen.getByText('Commerce')).toBeInTheDocument())
  await userEvent.click(screen.getByLabelText('close'))
  const painChip = screen.getByText('Latency')
  await userEvent.click(painChip)
  const painInput = await screen.findByLabelText('Pain point')
  await userEvent.clear(painInput)
  await waitFor(() => expect(screen.queryByText('Latency')).toBeNull())
  sessionStorage.clear()
})

test('chip clicks focus corresponding inputs', async () => {
  sessionStorage.setItem('industry', 'Fintech')
  sessionStorage.setItem('pain_point', 'Billing')
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () =>
      Response.json({ markdown: 'Hi', degraded: false }),
    ),
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
  const industryChip = await screen.findByText('Fintech')
  await userEvent.click(industryChip)
  const industryInput = await screen.findByLabelText('Industry')
  await waitFor(() => expect(industryInput).toHaveFocus())
  await userEvent.click(screen.getByLabelText('close'))
  const painChip = screen.getByText('Billing')
  await userEvent.click(painChip)
  const painInput = await screen.findByLabelText('Pain point')
  await waitFor(() => expect(painInput).toHaveFocus())
  await userEvent.click(screen.getByLabelText('close'))
  sessionStorage.clear()
})

test('context strength updates with field edits', async () => {
  sessionStorage.setItem('industry', 'Fintech')
  sessionStorage.setItem('pain_point', 'Billing')
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  server.use(
    http.post('/insight', async () =>
      Response.json({ markdown: 'Hi', degraded: false }),
    ),
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
  await screen.findByText('Context strength: High')
  const industryChip = screen.getByText('Fintech')
  await userEvent.click(industryChip)
  const industryInput = await screen.findByLabelText('Industry')
  await userEvent.clear(industryInput)
  await waitFor(() =>
    expect(screen.getByText('Context strength: Medium')).toBeInTheDocument(),
  )
  await userEvent.click(screen.getByLabelText('close'))
  const painChip = screen.getByText('Billing')
  await userEvent.click(painChip)
  const painInput = await screen.findByLabelText('Pain point')
  await userEvent.clear(painInput)
  await waitFor(() =>
    expect(screen.getByText('Context strength: Low')).toBeInTheDocument(),
  )
  sessionStorage.clear()
})
