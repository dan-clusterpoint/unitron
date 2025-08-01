import { render, screen } from '@testing-library/react'
import { test } from 'vitest'
import InsightCard from './InsightCard'

test('renders markdown', () => {
  const { container } = render(<InsightCard markdown="# Title\n\ntext" />)
  expect(container.querySelector('h1')).toBeInTheDocument()
})

test('shows skeleton when loading', () => {
  render(<InsightCard markdown="" loading />)
  expect(screen.getByTestId('insight-skeleton')).toBeInTheDocument()
})

test('shows fallback when markdown empty', () => {
  render(<InsightCard markdown="" />)
  expect(screen.getByText('Analysis unavailable')).toBeInTheDocument()
})
