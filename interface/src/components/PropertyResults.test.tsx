import { render, screen } from '@testing-library/react'
import { test } from 'vitest'
import PropertyResults from './PropertyResults'

const property = {
  confidence: 0.8,
}

test('renders confidence only', () => {
  render(<PropertyResults property={property} />)
  screen.getByText('80%')
  expect(screen.queryByText('example.com')).toBeNull()
  expect(screen.queryByText('note')).toBeNull()
})

