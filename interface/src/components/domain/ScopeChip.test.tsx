import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ScopeChip from './ScopeChip'
import { DomainProvider, useDomains } from '../../contexts/DomainContext'

function Wrapper() {
  const { addDomain } = useDomains()
  return (
    <div>
      <button onClick={() => addDomain('x.com')}>add</button>
      <ScopeChip />
    </div>
  )
}

test('updates count and toggles popover', async () => {
  const user = userEvent.setup()
  render(
    <DomainProvider>
      <Wrapper />
    </DomainProvider>,
  )
  const chip = screen.getByRole('button', { name: /Domains/ })
  expect(chip).toHaveTextContent('0 Domains')
  await user.click(screen.getByText('add'))
  expect(chip).toHaveTextContent('1 Domains')
  await user.click(chip)
  expect(await screen.findByRole('dialog')).toBeInTheDocument()
})
