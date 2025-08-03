import { renderHook, act } from '@testing-library/react'
import { DomainProvider, useDomains } from './DomainContext'

function setup() {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <DomainProvider>{children}</DomainProvider>
  )
  return renderHook(() => useDomains(), { wrapper })
}

test('crud operations', () => {
  const { result } = setup()
  act(() => result.current.addDomain('a.com'))
  expect(result.current.domains).toEqual(['a.com'])
  act(() => result.current.addDomain('b.com'))
  expect(result.current.domains).toEqual(['a.com', 'b.com'])
  act(() => result.current.removeDomain('a.com'))
  expect(result.current.domains).toEqual(['b.com'])
  act(() => result.current.setDomains(['c.com']))
  expect(result.current.domains).toEqual(['c.com'])
})
