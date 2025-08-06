import { render } from '@testing-library/react'
import { test, expect } from 'vitest'
import ExecutiveSummaryCard from './ExecutiveSummaryCard'

test('renders executive summary snapshot', () => {
  const { asFragment } = render(
    <ExecutiveSummaryCard
      profile={{
        name: 'Acme Inc',
        industry: 'SaaS',
        location: 'NYC',
        website: 'https://acme.com',
      }}
      score={75}
      risk={{ x: 1, y: 2 }}
      stack={[
        { label: 'React', status: 'added' },
        { label: 'Vue', status: 'removed' },
      ]}
      triggers={['Add chat widget', 'Improve SEO']}
      actions={[
        { label: 'Analyze stack', targetId: 'stack' },
        { label: 'Check risks', targetId: 'risk' },
      ]}
    />,
  )
  expect(asFragment()).toMatchSnapshot()
})
