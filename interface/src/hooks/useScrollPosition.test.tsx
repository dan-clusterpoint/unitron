/* eslint-disable @typescript-eslint/no-explicit-any */
import { renderHook } from '@testing-library/react'
import { act } from 'react'
import { test, expect } from 'vitest'
import useScrollPosition from './useScrollPosition'

test('updates scrolled and showTop based on window scroll', () => {
  Object.defineProperty(window, 'scrollY', { writable: true, value: 0 })
  const { result } = renderHook(() => useScrollPosition(10, 100))
  expect(result.current.scrolled).toBe(false)
  expect(result.current.showTop).toBe(false)

  act(() => {
    ;(window as any).scrollY = 20
    window.dispatchEvent(new Event('scroll'))
  })
  expect(result.current.scrolled).toBe(true)
  expect(result.current.showTop).toBe(false)

  act(() => {
    ;(window as any).scrollY = 150
    window.dispatchEvent(new Event('scroll'))
  })
  expect(result.current.showTop).toBe(true)
})
