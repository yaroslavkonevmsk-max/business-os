import { useState, useEffect, useCallback } from 'react'
import { loginWithTelegram } from '@/api/auth'
import { User } from '@/types'
import { getInitData, readyWebApp, expandWebApp } from '@/utils/telegram'

export function useAuth() {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const login = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const initData = getInitData()
      if (!initData) {
        setError('Telegram WebApp не инициализирован')
        setLoading(false)
        return
      }

      const response = await loginWithTelegram(initData)
      localStorage.setItem('jwt', response.access_token)
      setToken(response.access_token)
      setUser(response.user)
      readyWebApp()
      expandWebApp()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка авторизации')
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('jwt')
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    const storedToken = localStorage.getItem('jwt')
    if (storedToken) {
      setToken(storedToken)
      setLoading(false)
    } else {
      login()
    }

    const handleLogout = () => logout()
    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [login, logout])

  return { token, user, loading, error, login, logout }
}
