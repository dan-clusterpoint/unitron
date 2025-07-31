import { test, expect } from 'vitest'
import { parseInsightPayload } from './insightParser'

test('converts persona map to array', () => {
  const raw = { insight: { actions: [], evidence: '' }, personas: { p1: { name: 'P1' } }, degraded: false }
  const parsed = parseInsightPayload(raw)
  expect(parsed.personas).toEqual([{ id: 'p1', name: 'P1' }])
})

test('converts action map to array', () => {
  const raw = { insight: { actions: { a1: { title: 'T', reasoning: 'R', benefit: 'B' } }, evidence: 'E' }, personas: [], degraded: true }
  const parsed = parseInsightPayload(raw)
  expect(parsed.actions).toEqual([{ id: 'a1', title: 'T', reasoning: 'R', benefit: 'B' }])
  expect(parsed.degraded).toBe(true)
})

test('handles insights list with action field', () => {
  const raw = {
    insights: [
      { action: 'Do X', reasoning: 'Because' },
      { action: 'Do Y', reasoning: 'Why not' },
    ],
  }
  const parsed = parseInsightPayload(raw)
  expect(parsed.actions).toEqual([
    { id: '0', title: 'Do X', reasoning: 'Because', benefit: '' },
    { id: '1', title: 'Do Y', reasoning: 'Why not', benefit: '' },
  ])
})

test('ignores insight object evidence when only actions present', () => {
  const raw = { insight: { audience: 'X', insights: [{ action: 'A' }] } }
  const parsed = parseInsightPayload(raw)
  expect(parsed.actions.map((a) => a.title)).toEqual(['A'])
  expect(parsed.evidence).toBe('')
})
