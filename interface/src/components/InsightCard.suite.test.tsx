import { render, screen } from '@testing-library/react'
import { describe, test } from 'vitest'
import InsightCard from './InsightCard'
import type { ParsedInsight } from '../utils/insightParser'

describe('InsightCard', () => {
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

  test('falls back to persona id when name missing', () => {
    const insight: ParsedInsight = {
      evidence: '',
      personas: [{ id: 'p1' }],
      actions: [{ id: 'a1', title: 'Thing', reasoning: '', benefit: '' }],
      degraded: false,
    }
    render(<InsightCard insight={insight} />)
    screen.getByText('Thing')
    screen.getByText('p1')
  })
})
