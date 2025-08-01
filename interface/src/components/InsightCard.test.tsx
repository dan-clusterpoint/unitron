import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { test, vi } from 'vitest'
import InsightCard from './InsightCard'
import type { ParsedInsight } from '../utils/insightParser'

test('renders evidence, actions and personas', () => {
  const insight: ParsedInsight = {
    evidence: 'Proof',
    personas: [{ id: 'p1', name: 'P1', demographics: 'buyer' }],
    actions: [
      { id: 'a1', title: 'Do it', reasoning: 'why', benefit: 'gain' },
      { id: 'a2', title: 'Another', reasoning: '', benefit: '' },
    ],
    degraded: false,
  }
  render(<InsightCard insight={insight} />)
  screen.getByText('Proof')
  screen.getByText('Do it')
  screen.getByText('why')
  screen.getByText('gain')
  screen.getByText('Another')
  screen.getByText('P1')
  screen.getByText('buyer')
})

test('renders Not provided for missing persona fields', () => {
  const insight: ParsedInsight = {
    evidence: '',
    personas: [
      { id: 'p1', name: 'P1', demographics: '', company: null },
    ],
    actions: [],
    degraded: false,
  }
  render(<InsightCard insight={insight} />)
  screen.getByText(/demographics/i)
  screen.getByText(/company/i)
  expect(screen.getAllByText('Not provided')).toHaveLength(2)
})

test('copies markdown to clipboard and opens sheet', async () => {
  const write = vi.fn()
  Object.assign(navigator as any, { clipboard: { writeText: write } })
  const insight: ParsedInsight = {
    evidence: '',
    personas: [],
    actions: [{ id: '1', title: 'Act', reasoning: 'why', benefit: '' }],
    degraded: false,
  }
  render(<InsightCard insight={insight} />)
  await userEvent.click(screen.getByText('Copy Actions'))
  expect(write).toHaveBeenCalled()
  await userEvent.click(screen.getByText('View Markdown'))
  screen.getByText('Download Markdown')
})

test('shows skeleton when loading', () => {
  const insight: ParsedInsight = {
    evidence: '',
    personas: [],
    actions: [],
    degraded: false,
  }
  render(<InsightCard insight={insight} loading />)
  expect(screen.getByTestId('insight-skeleton')).toBeInTheDocument()
})

test('handles non-array inputs gracefully', () => {
  const insight = {
    evidence: 'x',
    personas: {} as any,
    actions: {} as any,
    degraded: false,
  }
  render(<InsightCard insight={insight as ParsedInsight} />)
  screen.getByText('No recommended actions were generated for this analysis.')
  screen.getByText('No data')
})

test('shows fallback message when no actions', () => {
  const insight: ParsedInsight = {
    evidence: 'Proof',
    personas: [{ id: 'p1', name: 'P1' }],
    actions: [],
    degraded: false,
  }
  render(<InsightCard insight={insight} />)
  screen.getByText('Proof')
  screen.getByText('P1')
  screen.getByText('No recommended actions were generated for this analysis.')
})
