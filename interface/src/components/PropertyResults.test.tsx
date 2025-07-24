import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import PropertyResults from './PropertyResults'

const property = {
  domains: ['example.com'],
  confidence: 0.8,
  notes: ['note'],
}

test('renders property fields', () => {
  render(<PropertyResults property={property} />)
  screen.getByText('example.com')
  screen.getByText('80%')
  screen.getByText('note')
})

