import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react-dom/test-utils'
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
      onAnalyze={async () => null}
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
      onAnalyze={async () => null}
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
  property: null,
  martech: {
    core: ['GTM'],
  },
  degraded: false,
}

test('renders AERIS dashboard above technology chips after analysis', async () => {
  vi.mock('../api', () => ({
    fetchAeris: vi.fn().mockResolvedValue({
      core_score: 10,
      signal_breakdown: [],
      degraded: false,
    }),
  }))
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  const onAnalyze = vi.fn().mockResolvedValue(null)
  const { rerender } = render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={onAnalyze}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={null}
    />,
  )
  await act(async () => {
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }))
    await onAnalyze.mock.results[0].value
  })
  rerender(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={onAnalyze}
      headless={false}
      setHeadless={() => {}}
      force={false}
      setForce={() => {}}
      loading={false}
      error=""
      result={result}
    />,
  )
  expect(await screen.findByText('AERIS Score')).toBeInTheDocument()
  expect(
    screen.getByRole('tab', { name: /Content Management System/i }),
  ).toBeInTheDocument()
  expect(screen.queryByText(/Analysis Result/i)).not.toBeInTheDocument()
})

test('shows degraded banner', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={async () => null}
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

test('counts nested martech buckets correctly', () => {
  const nested: AnalyzeResult = {
    property: { domains: [], confidence: 0.5, notes: [] },
    martech: { core: ['A'], adjacent: { one: {}, two: {} } },
    degraded: false,
  }
  expect(computeMartechCount(nested.martech)).toBe(3)
})

