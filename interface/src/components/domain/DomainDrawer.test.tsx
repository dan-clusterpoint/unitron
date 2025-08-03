import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DomainDrawer from './DomainDrawer'
import { DomainProvider, useDomains } from '../../contexts/DomainContext'

function Wrapper({ rerun }: { rerun: () => void }) {
  const { domains } = useDomains()
  return (
    <div>
      <div data-testid="count">{domains.length}</div>
      <DomainDrawer onClose={() => {}} onRerun={rerun} />
    </div>
  )
}

test('save rerun updates domains, tracks, and calls rerun', async () => {
  const user = userEvent.setup()
  const log = vi.spyOn(console, 'log').mockImplementation(() => {})
  const rerun = vi.fn()
  render(
    <DomainProvider initial={['a.com']}>
      <Wrapper rerun={rerun} />
    </DomainProvider>,
  )
  const textarea = screen.getByRole('textbox')
  await user.clear(textarea)
  await user.type(textarea, 'b.com')
  await user.click(screen.getByRole('button', { name: /save/i }))
  expect(screen.getByTestId('count')).toHaveTextContent('1')
  expect(log).toHaveBeenCalledWith('track', 'analysis_rerun', undefined)
  expect(rerun).toHaveBeenCalled()
  log.mockRestore()
})
