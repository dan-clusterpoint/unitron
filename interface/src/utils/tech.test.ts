import { describe, it, expect } from 'vitest'
import { normalizeTechList, normalizeStack } from './tech'

describe('normalizeTechList', () => {
  it('trims, dedupes case-insensitively, and removes empty', () => {
    const input = ['  GA4 ', 'ga4', 'Adobe', '', 'ADOBE', 'Mixpanel']
    expect(normalizeTechList(input)).toEqual(['GA4', 'Adobe', 'Mixpanel'])
  })

  it('coerces falsy values to empty array', () => {
    expect(normalizeTechList([undefined, null, '  '])).toEqual([])
  })
})

describe('normalizeStack', () => {
  it('maps aliases, assigns categories, and dedupes case-insensitively', () => {
    const input = ['ga', 'AEM', 'GA4', 'GTM', 'google tag manager']
    expect(normalizeStack(input)).toEqual([
      { category: 'Tagging & Analytics', vendor: 'Google Analytics 4' },
      { category: 'Web Platform', vendor: 'Adobe Experience Manager' },
      { category: 'Tagging & Analytics', vendor: 'Google Tag Manager' },
    ])
  })

  it('coerces falsy values to empty array', () => {
    expect(normalizeStack([undefined, null, '  '])).toEqual([])
  })
})
