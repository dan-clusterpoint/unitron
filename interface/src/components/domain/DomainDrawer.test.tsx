import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DomainDrawer from './DomainDrawer'
import { DomainProvider, useDomains } from '../../contexts/DomainContext'

function Wrapper() {
  const { domains } = useDomains()
  return (
    <div>
      <div data-testid="count">{domains.length}</div>
      <DomainDrawer onClose={() => {}} />
    </div>
  )
}

test('save rerun updates domains and tracks', async () => {
  const user = userEvent.setup()
  const log = vi.spyOn(console, 'log').mockImplementation(() => {})
  render(
    <DomainProvider initial={['a.com']}>
      <Wrapper />
    </DomainProvider>,
  )
  const textarea = screen.getByRole('textbox')
  await user.clear(textarea)
  await user.type(textarea, 'b.com')
  await user.click(screen.getByRole('button', { name: /save/i }))
  expect(screen.getByTestId('count')).toHaveTextContent('1')
  expect(log).toHaveBeenCalledWith('track', 'analysis_rerun', undefined)
  log.mockRestore()
})
