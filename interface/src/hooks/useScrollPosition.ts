import { useEffect, useState } from 'react'

/**
 * Track scroll position to toggle UI elements.
 * @param threshold Y offset to mark page as scrolled
 * @param topThreshold Y offset to show "back to top" button
 */
export default function useScrollPosition(
  threshold = 10,
  topThreshold = 200,
) {
  const [scrolled, setScrolled] = useState(false)
  const [showTop, setShowTop] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > threshold)
      setShowTop(window.scrollY > topThreshold)
    }
    onScroll()
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [threshold, topThreshold])

  return { scrolled, showTop }
}
