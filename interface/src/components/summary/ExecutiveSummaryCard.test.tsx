import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import ExecutiveSummaryCard from './ExecutiveSummaryCard'

test('renders executive summary snapshot', () => {
  const { asFragment } = render(
    <ExecutiveSummaryCard
      profile={{
        name: 'Acme Inc',
        tagline: 'We build stuff',
        industry: 'SaaS',
        location: 'NYC',
        website: 'https://acme.com',
        logoUrl: 'https://logo.example.com/acme.png',
      }}
      score={75}
      vendors={['React', 'Vue']}
      triggers={['Add chat widget', 'Improve SEO']}
      seo={{ robotsTxt: true, sitemapXml: false }}
    />,
  )
  expect(screen.getByAltText('Acme Inc logo')).toBeInTheDocument()
  expect(screen.getByTestId('seo-basics')).toHaveTextContent(
    /Robots\.txt ✓/,
  )
  expect(screen.getByTestId('seo-basics')).toHaveTextContent(/Sitemap ✗/)
  expect(asFragment()).toMatchSnapshot()
})

test('omits sections when data is missing', () => {
  const { asFragment, queryAllByTestId, container } = render(
    <ExecutiveSummaryCard
      profile={{
        name: 'Acme Inc',
        tagline: 'We build stuff',
        industry: 'SaaS',
        location: 'NYC',
        website: 'https://acme.com',
        logoUrl: 'https://logo.example.com/acme.png',
      }}
      score={75}
      vendors={[]}
      triggers={[]}
    />,
  )
  expect(container.querySelector('.xs\\:col-span-2.space-y-1')).toBeNull()
  expect(queryAllByTestId('growth-trigger')).toHaveLength(0)
  expect(screen.queryByTestId('seo-basics')).toBeNull()
  expect(asFragment()).toMatchSnapshot()
})
