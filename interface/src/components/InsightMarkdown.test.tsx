import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import InsightMarkdown from './InsightMarkdown'

test('renders markdown', () => {
  const { container } = render(<InsightMarkdown markdown="# Title\n\ntext" />)
  expect(container.querySelector('h1')).toBeInTheDocument()
})

test('sanitizes html', () => {
  const { container } = render(
    <InsightMarkdown markdown={'<script>alert(1)</script><b>hi</b>'} />,
  )
  expect(container.querySelector('script')).toBeNull()
  expect(container.querySelector('b')).toBeInTheDocument()
})

test('shows skeleton when loading', () => {
  render(<InsightMarkdown markdown="" loading />)
  expect(screen.getByTestId('insight-skeleton')).toBeInTheDocument()
})

test('shows fallback when markdown empty', () => {
  render(<InsightMarkdown markdown="" />)
  expect(screen.getByText('Analysis unavailable')).toBeInTheDocument()
  expect(
    screen.queryByRole('button', { name: /export markdown/i }),
  ).toBeNull()
})

test('shows degraded banner', () => {
  render(<InsightMarkdown markdown="# H" degraded />)
  expect(screen.getByText(/Partial results/)).toBeInTheDocument()
})

test('shows export button when markdown provided', () => {
  render(<InsightMarkdown markdown="# H" />)
  expect(
    screen.getByRole('button', { name: /export markdown/i }),
  ).toBeInTheDocument()
})
