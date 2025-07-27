import { render, screen } from '@testing-library/react'
import { test } from 'vitest'
import CmsResults from './CmsResults'

test('renders cms names', () => {
  render(<CmsResults cms={['WordPress', 'Drupal']} />)
  screen.getByText('WordPress')
  screen.getByText('Drupal')
})

test('shows fallback when empty', () => {
  render(<CmsResults cms={[]} />)
  screen.getByText('Nothing detected')
})
