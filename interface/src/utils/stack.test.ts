import { describe, it, expect } from 'vitest'
import { normalizeStackInput } from './stack'

describe('normalizeStackInput', () => {
  it('resolves synonyms case-insensitively', () => {
    expect(normalizeStackInput('aem')).toEqual({
      vendor: 'Adobe Experience Manager',
      category: 'Web Platform',
    })
  })

  it('returns Uncategorized when unknown', () => {
    expect(normalizeStackInput('MyTool')).toEqual({
      vendor: 'MyTool',
      category: 'Uncategorized',
    })
  })
})
