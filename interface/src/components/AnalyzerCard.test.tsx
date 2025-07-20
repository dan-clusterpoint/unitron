import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import AnalyzerCard from './AnalyzerCard'

test('shows spinner when loading', () => {
  const { container } = render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
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
      loading={false}
      error="oops"
      result={null}
    />,
  )
  expect(screen.getByText('oops')).toBeInTheDocument()
})

const result = {
  domains: ['example.com'],
  confidence: 1,
  notes: ['note'],
}

test('renders result lists', () => {
  render(
    <AnalyzerCard
      id="a"
      url="foo"
      setUrl={() => {}}
      onAnalyze={() => {}}
      loading={false}
      error=""
      result={result}
    />,
  )
  expect(screen.getByText('example.com')).toBeInTheDocument()
})
