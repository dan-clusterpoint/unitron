import type { Meta, StoryObj } from '@storybook/react'
import DomainDrawer from './DomainDrawer'
import { DomainProvider } from '../../contexts/DomainContext'

const meta: Meta<typeof DomainDrawer> = {
  component: DomainDrawer,
}
export default meta

type Story = StoryObj<typeof DomainDrawer>

export const Open: Story = {
  render: () => (
    <DomainProvider initial={['example.com','foo.com']}>
      <DomainDrawer onClose={() => {}} />
    </DomainProvider>
  ),
}
