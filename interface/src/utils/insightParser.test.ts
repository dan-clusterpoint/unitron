import { test, expect } from 'vitest'
import { parseInsightPayload } from './insightParser'

test('converts persona map to array', () => {
  const raw = { insight: { actions: [], evidence: '' }, personas: { p1: { name: 'P1' } }, degraded: false }
  const parsed = parseInsightPayload(raw)
  expect(parsed.personas).toEqual([
    { id: 'p1', name: 'P1', demographics: 'unknown', needs: 'unknown', goals: 'unknown' },
  ])
})

test('defaults missing persona fields to unknown', () => {
  const raw = { insight: { actions: [], evidence: '' }, personas: [{ id: 'p1', name: 'P1' }], degraded: false }
  const parsed = parseInsightPayload(raw)
  expect(parsed.personas).toEqual([
    { id: 'p1', name: 'P1', demographics: 'unknown', needs: 'unknown', goals: 'unknown' },
  ])
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
    personas: [
      { id: 'p1', name: 'P1', demographics: 'unknown', needs: 'unknown', goals: 'unknown' },
    ],
    degraded: false,
  })
})

test('handles NextBestAction nested in evidence', () => {
  const raw = {
    insight: {
      actions: [],
      evidence: {
        NextBestAction: { title: 'T', reasoning: 'R', benefit: 'B' },
        Persona: { id: 'p2', name: 'P2' },
        evidence: 'E',
      },
    },
    personas: [{ id: 'p1', name: 'P1' }],
    degraded: false,
  }
  const parsed = parseInsightPayload(raw)
  expect(parsed.actions).toEqual([{ id: '1', title: 'T', reasoning: 'R', benefit: 'B' }])
  expect(parsed.personas).toEqual([
    { id: 'p1', name: 'P1', demographics: 'unknown', needs: 'unknown', goals: 'unknown' },
    { id: 'p2', name: 'P2', demographics: 'unknown', needs: 'unknown', goals: 'unknown' },
  ])
  expect(parsed.evidence).toBe('E')
})

