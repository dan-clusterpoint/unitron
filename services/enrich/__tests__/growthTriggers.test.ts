import assert from 'node:assert'
import { z } from 'zod'
import { GrowthTriggerSchema } from '../growthTriggers'

const GrowthTriggerArray = z.array(GrowthTriggerSchema).max(3)

const valid = [
  { title: 'A', description: 'Alpha' },
  { title: 'B', description: 'Beta' },
  { title: 'C', description: 'Gamma' },
]
assert.deepStrictEqual(GrowthTriggerArray.parse(valid), valid)

const tooMany = [
  { title: 'A', description: 'Alpha' },
  { title: 'B', description: 'Beta' },
  { title: 'C', description: 'Gamma' },
  { title: 'D', description: 'Delta' },
]
assert.throws(() => GrowthTriggerArray.parse(tooMany))

const invalid = [
  { title: 'A', description: 'Alpha' },
  { title: 'B' } as any,
]
assert.throws(() => GrowthTriggerArray.parse(invalid))

console.log('GrowthTriggerArray tests passed')
