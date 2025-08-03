import type { Meta, StoryObj } from '@storybook/react'
import ScopeChip from './ScopeChip'
import { DomainProvider } from '../../contexts/DomainContext'

const meta: Meta<typeof ScopeChip> = {
  component: ScopeChip,
  args: { onRerun: () => {} },
}
export default meta

type Story = StoryObj<typeof ScopeChip>

export const Empty: Story = {
  decorators: [(Story) => (<DomainProvider><Story /></DomainProvider>)],
}

export const Populated: Story = {
  decorators: [
    (Story) => (
      <DomainProvider initial={['example.com', 'test.com']}>
        <Story />
      </DomainProvider>
    ),
  ],
}
