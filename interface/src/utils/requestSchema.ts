import { z } from 'zod'

export const requestSchema = z.object({
  url: z.string().url(),
  martech: z.object({
    core: z.array(z.string()),
    adjacent: z.array(z.string()),
    broader: z.array(z.string()),
    competitors: z.array(z.string()),
  }),
  cms: z.array(z.string()),
  industry: z.string().max(1024).optional(),
  pain_point: z.string().max(1024).optional(),
  stack: z
    .array(z.object({ category: z.string(), vendor: z.string() }))
    .optional()
    .default([]),
  evidence_standards: z.string().max(1024),
  credibility_scoring: z.string().max(1024),
  deliverable_guidelines: z.string().max(1024),
  audience: z.string().max(1024),
  preferences: z.string().max(1024),
})

export type RequestSchema = z.infer<typeof requestSchema>
