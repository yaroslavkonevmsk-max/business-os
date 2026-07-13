export interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
}

export const getTelegramWebApp = (): TelegramWebApp | null => {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp
  }
  return null
}

export const getInitData = (): string => {
  const webApp = getTelegramWebApp()
  if (!webApp) {
    return ''
  }
  return webApp.initData
}

export const getTelegramUser = (): TelegramUser | null => {
  const webApp = getTelegramWebApp()
  if (!webApp) {
    return null
  }
  return webApp.initDataUnsafe.user ?? null
}

export const expandWebApp = (): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.expand()
  }
}

export const readyWebApp = (): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.ready()
  }
}

export const setHeaderColor = (color: string): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.setHeaderColor(color as 'bg_color' | 'secondary_bg_color')
  }
}

export const setBackgroundColor = (color: string): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.setBackgroundColor(color as 'bg_color' | 'secondary_bg_color')
  }
}

export const openTelegramLink = (url: string): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.openTelegramLink(url)
  } else {
    window.open(url, '_blank')
  }
}

export const openExternalLink = (url: string): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.openLink(url)
  } else {
    window.open(url, '_blank')
  }
}

export const getThemeParams = (): ThemeParams => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    return webApp.themeParams
  }
  return {
    bg_color: '#ffffff',
    text_color: '#000000',
    hint_color: '#999999',
    link_color: '#2481cc',
    button_color: '#2481cc',
    button_text_color: '#ffffff',
    secondary_bg_color: '#f5f5f5',
  }
}

export const isDarkTheme = (): boolean => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    return webApp.colorScheme === 'dark'
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const hapticFeedback = (
  type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' | 'success' | 'warning' | 'error'
): void => {
  const webApp = getTelegramWebApp()
  if (!webApp?.HapticFeedback) return

  if (type === 'success' || type === 'warning' || type === 'error') {
    webApp.HapticFeedback.notificationOccurred(type)
  } else {
    webApp.HapticFeedback.impactOccurred(type)
  }
}

export const showMainButton = (text: string, onClick: () => void, color?: string, textColor?: string): void => {
  const webApp = getTelegramWebApp()
  if (!webApp?.MainButton) return

  webApp.MainButton.setText(text)
  if (color) webApp.MainButton.setParams({ color })
  if (textColor) webApp.MainButton.setParams({ text_color: textColor })
  webApp.MainButton.onClick(onClick)
  webApp.MainButton.show()
}

export const hideMainButton = (): void => {
  const webApp = getTelegramWebApp()
  if (webApp?.MainButton) {
    webApp.MainButton.hide()
    webApp.MainButton.offClick(() => {})
  }
}

export const showBackButton = (onClick: () => void): void => {
  const webApp = getTelegramWebApp()
  if (!webApp?.BackButton) return
  webApp.BackButton.onClick(onClick)
  webApp.BackButton.show()
}

export const hideBackButton = (): void => {
  const webApp = getTelegramWebApp()
  if (webApp?.BackButton) {
    webApp.BackButton.hide()
    webApp.BackButton.offClick(() => {})
  }
}

export const closeWebApp = (): void => {
  const webApp = getTelegramWebApp()
  if (webApp) {
    webApp.close()
  }
}

export const shareToTelegram = (text: string, url?: string): void => {
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url || window.location.href)}&text=${encodeURIComponent(text)}`
  openTelegramLink(shareUrl)
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp
    }
  }
}

// Minimal Telegram WebApp types to avoid relying solely on @types/telegram-web-app
interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramUser
    query_id?: string
    auth_date?: number
    hash?: string
    start_param?: string
  }
  colorScheme: 'light' | 'dark'
  themeParams: ThemeParams
  ready: () => void
  expand: () => void
  close: () => void
  setHeaderColor: (color: 'bg_color' | 'secondary_bg_color') => void
  setBackgroundColor: (color: 'bg_color' | 'secondary_bg_color') => void
  openLink: (url: string, options?: { try_instant_view?: boolean }) => void
  openTelegramLink: (url: string) => void
  MainButton: MainButton
  BackButton: BackButton
  HapticFeedback: HapticFeedback
}

interface ThemeParams {
  bg_color?: string
  text_color?: string
  hint_color?: string
  link_color?: string
  button_color?: string
  button_text_color?: string
  secondary_bg_color?: string
  header_bg_color?: string
  accent_text_color?: string
  destructive_text_color?: string
  subtitle_text_color?: string
  section_bg_color?: string
  section_header_text_color?: string
  section_separator_color?: string
}

interface MainButton {
  text: string
  setText: (text: string) => void
  onClick: (callback: () => void) => void
  offClick: (callback: () => void) => void
  show: () => void
  hide: () => void
  enable: () => void
  disable: () => void
  setParams: (params: { color?: string; text_color?: string }) => void
}

interface BackButton {
  isVisible: boolean
  onClick: (callback: () => void) => void
  offClick: (callback: () => void) => void
  show: () => void
  hide: () => void
}

interface HapticFeedback {
  impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
  notificationOccurred: (type: 'error' | 'success' | 'warning') => void
  selectionChanged: () => void
}
