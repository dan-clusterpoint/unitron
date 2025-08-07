import { render, screen } from '@testing-library/react'
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
        logoUrl: 'https://logo.example.com/acme.png',
      }}
      score={75}
      risk={{ x: 1, y: 2, level: 'high' }}
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
  expect(screen.getByAltText('Acme Inc logo')).toBeInTheDocument()
  expect(asFragment()).toMatchSnapshot()
})

test('omits sections when data is missing', () => {
  const {
    asFragment,
    queryByLabelText,
    queryAllByTestId,
    container,
  } = render(
    <ExecutiveSummaryCard
      profile={{
        name: 'Acme Inc',
        industry: 'SaaS',
        location: 'NYC',
        website: 'https://acme.com',
        logoUrl: 'https://logo.example.com/acme.png',
      }}
      score={75}
      stack={[]}
      triggers={[]}
      actions={[]}
    />,
  )
  expect(queryByLabelText('healthchecks')).toBeNull()
  expect(container.querySelector('.xs\\:col-span-2.space-y-1')).toBeNull()
  expect(queryAllByTestId('growth-trigger')).toHaveLength(0)
  expect(container.querySelector('ul.flex.flex-wrap.gap-2')).toBeNull()
  expect(asFragment()).toMatchSnapshot()
})
