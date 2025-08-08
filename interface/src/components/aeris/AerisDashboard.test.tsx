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
}

test('renders AerisDashboard snapshot', () => {
  const { asFragment } = render(<AerisDashboard data={mockData} />)
  expect(asFragment()).toMatchSnapshot()
})
