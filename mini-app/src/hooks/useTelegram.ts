import { useCallback, useEffect, useRef } from 'react'
import {
  getTelegramWebApp,
  hapticFeedback,
  showMainButton,
  hideMainButton,
  showBackButton,
  hideBackButton,
  isDarkTheme,
} from '@/utils/telegram'

export function useTelegram() {
  const webApp = useRef(getTelegramWebApp())

  const haptic = useCallback(
    (type: Parameters<typeof hapticFeedback>[0]) => {
      hapticFeedback(type)
    },
    []
  )

  const showMainBtn = useCallback(
    (text: string, onClick: () => void, color?: string, textColor?: string) => {
      showMainButton(text, onClick, color, textColor)
    },
    []
  )

  const hideMainBtn = useCallback(() => {
    hideMainButton()
  }, [])

  const showBackBtn = useCallback(
    (onClick: () => void) => {
      showBackButton(onClick)
    },
    []
  )

  const hideBackBtn = useCallback(() => {
    hideBackButton()
  }, [])

  useEffect(() => {
    return () => {
      hideMainButton()
      hideBackButton()
    }
  }, [])

  return {
    webApp: webApp.current,
    haptic,
    showMainButton: showMainBtn,
    hideMainButton: hideMainBtn,
    showBackButton: showBackBtn,
    hideBackButton: hideBackBtn,
    isDark: isDarkTheme(),
  }
}
