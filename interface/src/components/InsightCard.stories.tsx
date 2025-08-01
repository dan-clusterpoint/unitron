import type { Meta, StoryObj } from '@storybook/react'
import InsightCard from './InsightCard'

const meta: Meta<typeof InsightCard> = {
  title: 'Components/InsightCard',
  component: InsightCard,
}
export default meta

const sample = `# Opportunities\n\n- Add schema.org markup\n- Compress images`

export const Default: StoryObj<typeof InsightCard> = {
  args: { markdown: sample },
}
