import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import AnalyzerCard, { type AnalyzeResult } from './AnalyzerCard'

test('shows spinner when loading', () => {
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

test('displays error message', () => {
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

test('renders result lists', () => {
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

test('shows degraded banner', () => {
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
