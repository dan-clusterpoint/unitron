import { useState } from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MartechCategorySelector, { type MartechItem } from './MartechCategorySelector'

test('select and deselect vendor', async () => {
  const user = userEvent.setup()
  const handle = vi.fn()
  function Wrapper() {
    const [val, setVal] = useState<MartechItem[]>([])
    return (
      <MartechCategorySelector
        value={val}
        onChange={(v) => {
          setVal(v)
          handle(v)
        }}
      />
    )
  }
  render(<Wrapper />)
  const analyticsTab = screen.getByRole('tab', { name: /Web \/ Product Analytics/i })
  await user.click(analyticsTab)
  const ga = screen.getByLabelText('Google Analytics') as HTMLInputElement
  await user.click(ga)
  expect(handle).toHaveBeenLastCalledWith([
    { category: 'analytics', vendor: 'Google Analytics' },
  ])
  await user.click(ga)
  expect(handle).toHaveBeenLastCalledWith([])
})

test('add vendor via other input', async () => {
  const user = userEvent.setup()
  const handle = vi.fn()
  function Wrapper() {
    const [val, setVal] = useState<MartechItem[]>([])
    return (
      <MartechCategorySelector
        value={val}
        onChange={(v) => {
          setVal(v)
          handle(v)
        }}
      />
    )
  }
  render(<Wrapper />)
  const input = screen.getByLabelText('cms-other')
  await user.type(input, 'NewCMS{enter}')
  expect(handle).toHaveBeenLastCalledWith([
    { category: 'cms', vendor: 'NewCMS' },
  ])
})
