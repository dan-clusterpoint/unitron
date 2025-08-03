import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import EditableMartechList from './EditableMartechList'

test('renders initial vendors and supports add/remove', async () => {
  const handle = vi.fn()
  render(<EditableMartechList value={['GA']} onChange={handle} />)
  expect(screen.getByDisplayValue('GA')).toBeInTheDocument()
  const input = screen.getByLabelText('add vendor')
  await userEvent.type(input, 'Segment{enter}')
  expect(handle).toHaveBeenLastCalledWith(['GA', 'Segment'])
  const remove = screen.getByLabelText('remove GA')
  await userEvent.click(remove)
  expect(handle).toHaveBeenLastCalledWith([])
})
