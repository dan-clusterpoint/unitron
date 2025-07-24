import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import MartechResults from './MartechResults'

test('shows fallback when empty', () => {
  render(<MartechResults martech={{}} />)
  screen.getByText('Nothing detected')
})

test('renders vendor groups', () => {
  render(<MartechResults martech={{ core: ['A'], adjacent: [], broader: [], competitors: ['B'] }} />)
  screen.getByText('A')
  screen.getByText('B')
})

