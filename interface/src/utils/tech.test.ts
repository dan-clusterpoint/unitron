import { describe, it, expect } from 'vitest'
import { normalizeTechList } from './tech'

describe('normalizeTechList', () => {
  it('trims, dedupes case-insensitively, and removes empty', () => {
    const input = ['  GA4 ', 'ga4', 'Adobe', '', 'ADOBE', 'Mixpanel']
    expect(normalizeTechList(input)).toEqual(['GA4', 'Adobe', 'Mixpanel'])
  })

  it('coerces falsy values to empty array', () => {
    expect(normalizeTechList([undefined, null, '  '])).toEqual([])
  })
})
