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

test('parses canonical fields', () => {
  const raw = {
    insight: { actions: [{ title: 'T', reasoning: 'R', benefit: 'B' }], evidence: 'E' },
    personas: [{ id: 'p1', name: 'P1' }],
    degraded: false,
  }
  const parsed = parseInsightPayload(raw)
  expect(parsed).toEqual({
    actions: [{ id: '1', title: 'T', reasoning: 'R', benefit: 'B' }],
    evidence: 'E',
    personas: [{ id: 'p1', name: 'P1' }],
    degraded: false,
  })
})

