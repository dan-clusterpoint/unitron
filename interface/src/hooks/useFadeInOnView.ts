import { useEffect } from 'react'

/**
 * Apply the `fade-in` class to elements once they enter the viewport.
 * Elements are selected using the provided selector.
 */
export default function useFadeInOnView(selector = '[data-observe]') {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) e.target.classList.add('fade-in')
        })
      },
      { threshold: 0.1 },
    )

    document.querySelectorAll<HTMLElement>(selector).forEach((el) =>
      observer.observe(el),
    )
    return () => observer.disconnect()
  }, [selector])
}
