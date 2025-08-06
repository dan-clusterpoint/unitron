import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import type { AnalyzeResult, Snapshot } from './AnalyzerCard'
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
      snapshot={null}
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
      snapshot={null}
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
      snapshot={null}
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
      snapshot={null}
    />,
  )
  expect(screen.getByText(/partial results/i)).toBeInTheDocument()
})

test('renders snapshot when provided', async () => {
  const { default: AnalyzerCard } = await import('./AnalyzerCard')
  const snap: Snapshot = {
    profile: { name: 'Acme' },
    digitalScore: 75,
    stackDelta: [],
    growthTriggers: [],
    nextActions: [],
  }
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
      snapshot={snap}
    />,
  )
  expect(screen.getByText('Acme')).toBeInTheDocument()
})

test('counts nested martech buckets correctly', () => {
  const nested: AnalyzeResult = {
    property: { domains: [], confidence: 0.5, notes: [] },
    martech: { core: ['A'], adjacent: { one: {}, two: {} } },
    degraded: false,
  }
  expect(computeMartechCount(nested.martech)).toBe(3)
})

