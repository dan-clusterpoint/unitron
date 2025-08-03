import type { Meta, StoryObj } from '@storybook/react'
import DomainPopover from './DomainPopover'
import ScopeChip from './ScopeChip'
import { DomainProvider } from '../../contexts/DomainContext'

const meta: Meta<typeof DomainPopover> = {
  component: DomainPopover,
}
export default meta

type Story = StoryObj<typeof DomainPopover>

export const WithChip: Story = {
  render: () => (
    <DomainProvider initial={['example.com', 'test.com']}>
      <ScopeChip onRerun={() => {}} />
    </DomainProvider>
  ),
}