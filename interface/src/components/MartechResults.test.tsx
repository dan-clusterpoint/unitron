import { render, screen } from '@testing-library/react'
import { test } from 'vitest'
import MartechResults from './MartechResults'
import CmsResults from './CmsResults'

test('shows fallback when empty', () => {
  render(<MartechResults martech={{}} />)
  screen.getByText('Nothing detected')
})

test('renders vendor groups', () => {
  render(<MartechResults martech={{ core: ['A'], adjacent: [], broader: [], competitors: ['B'] }} />)
  screen.getByText('A')
  screen.getByText('B')
})

test('renders cms names', () => {
  render(<CmsResults cms={['WordPress', 'AEM']} />)
  screen.getByText('WordPress')
  screen.getByText('AEM')
})

