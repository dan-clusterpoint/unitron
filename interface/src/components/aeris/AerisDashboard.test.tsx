import { render } from '@testing-library/react'
import { test, expect } from 'vitest'
import AerisDashboard from './AerisDashboard'

const mockData = {
  core_score: 42,
  signal_breakdown: [
    { name: 'Signal A', score: 80 },
    { name: 'Signal B', score: 20 },
  ],
  peers: [{ name: 'Peer 1', score: 50 }],
  variants: [{ name: 'V1', score: 30 }],
  opportunities: ['Opportunity 1'],
  narratives: ['Narrative 1'],
  degraded: false,
}

test('renders AerisDashboard snapshot', () => {
  const { asFragment } = render(<AerisDashboard data={mockData} />)
  expect(asFragment()).toMatchSnapshot()
})

test('shows unavailable when degraded', () => {
  const { getByText } = render(
    <AerisDashboard data={{ ...mockData, degraded: true }} />
  )
  getByText('AERIS unavailable')
})

test('shows unavailable when core_score missing', () => {
  const { core_score, ...rest } = mockData
  const { getByText } = render(
    <AerisDashboard data={{ ...rest } as any} />
  )
  getByText('AERIS unavailable')
})
