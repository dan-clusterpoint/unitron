import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import { server } from '../setupTests'
import { http } from 'msw'
import AnalysisResultPage from './AnalysisResultPage'

test('renders ExecutiveSummaryCard when snapshot data present without legacy exec-summary section', async () => {
  server.use(
    http.post('http://localhost:8080/snapshot', () =>
      Response.json({
        snapshot: {
          profile: {
            name: 'Acme Inc',
            industry: 'SaaS',
            location: 'NYC',
            website: 'https://acme.com',
          },
          digitalScore: 80,
          riskMatrix: { x: 1, y: 2 },
          stackDelta: [{ label: 'React', status: 'added' }],
          growthTriggers: ['Improve SEO'],
          nextActions: [{ label: 'Analyze stack', targetId: 'stack' }],
        },
      }),
    ),
  )

  render(<AnalysisResultPage />)
  await screen.findByRole('heading', { name: /Executive Summary/i })
  expect(screen.getByText('Acme Inc')).toBeInTheDocument()
  expect(document.querySelector('#exec-summary')).toBeNull()
})
