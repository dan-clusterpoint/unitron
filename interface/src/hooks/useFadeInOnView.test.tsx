import { render } from '@testing-library/react'
import { vi, beforeEach, afterEach, test, expect } from 'vitest'
import useFadeInOnView from './useFadeInOnView'

class MockObserver {
  observe = vi.fn()
  disconnect = vi.fn()
  constructor(public cb: IntersectionObserverCallback) {}
}

let instance: MockObserver

beforeEach(() => {
  global.IntersectionObserver = vi
    .fn((cb) => {
      instance = new MockObserver(cb)
      return instance as unknown as IntersectionObserver
    }) as unknown as typeof IntersectionObserver
})

afterEach(() => {
  ;(global.IntersectionObserver as any) = undefined
})

test('adds fade-in class when element intersects', () => {
  const Test = () => {
    useFadeInOnView('[data-test]')
    return <div data-test></div>
  }
  const { container } = render(<Test />)
  const el = container.querySelector('[data-test]') as HTMLElement
  expect(instance.observe).toHaveBeenCalledWith(el)

  instance.cb([{ target: el, isIntersecting: true } as any])
  expect(el.classList.contains('fade-in')).toBe(true)
})
