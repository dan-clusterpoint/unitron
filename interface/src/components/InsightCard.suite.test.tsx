import { render, screen } from '@testing-library/react'
import { describe, test } from 'vitest'
import InsightCard from './InsightCard'
import type { ParsedInsight } from '../utils/insightParser'

describe('InsightCard', () => {
  test('renders summary, actions and personas', () => {
    const insight: ParsedInsight = {
      summary: 'My summary',
      personas: [{ id: 'p1', name: 'P1', role: 'buyer' }],
      actions: [
        { description: 'Do it', persona: 'p1', evidence: ['src'] },
        { description: 'Another' },
      ],
    }
    render(<InsightCard insight={insight} />)
    screen.getByText('My summary')
    screen.getByText('Do it')
    screen.getByText('Another')
    screen.getByText('src')
    screen.getByText('P1')
    screen.getByText('buyer')
  })

  test('falls back to persona id when name missing', () => {
    const insight: ParsedInsight = {
      summary: '',
      personas: [{ id: 'p1' }],
      actions: [{ description: 'Thing', persona: 'p1' }],
    }
    render(<InsightCard insight={insight} />)
    screen.getByText('p1:')
    screen.getByText('Thing')
  })
})
