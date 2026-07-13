import { useEffect, useState } from 'react'
import { isDarkTheme } from '@/utils/telegram'

export function useTheme() {
  const [dark, setDark] = useState(isDarkTheme())

  useEffect(() => {
    const updateTheme = () => {
      const isDark = isDarkTheme()
      setDark(isDark)
      if (isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }

    updateTheme()

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', updateTheme)

    return () => {
      mediaQuery.removeEventListener('change', updateTheme)
    }
  }, [])

  return { dark }
}
