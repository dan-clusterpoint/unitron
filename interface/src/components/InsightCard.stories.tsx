import type { Meta, StoryObj } from '@storybook/react'
import InsightCard from './InsightCard'
import type { ParsedInsight } from '../utils/insightParser'

const meta: Meta<typeof InsightCard> = {
  title: 'Components/InsightCard',
  component: InsightCard,
}
export default meta

const sample: ParsedInsight = {
  evidence: 'We found multiple opportunities to improve.',
  actions: [
    { id: 'a1', title: 'Add schema.org markup', reasoning: 'Helps SEO', benefit: 'More traffic' },
    { id: 'a2', title: 'Compress images', reasoning: 'Speeds up load time', benefit: 'Better UX' },
  ],
  personas: [
    { id: 'p1', name: 'The Marketer', demographics: '25-40', goals: 'Drive leads' },
    { id: 'p2', name: 'The Engineer', demographics: '30+', goals: 'Maintain site' },
  ],
  degraded: false,
}

export const Default: StoryObj<typeof InsightCard> = {
  args: { insight: sample },
}
