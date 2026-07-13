import { createContext, useContext, ReactNode, useState, useCallback } from 'react'
import { User } from '@/types'
import { useAuth } from '@/hooks/useAuth'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
  isAuthenticated: boolean
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const { token, user, loading, error, login, logout } = useAuth()
  const [authUser, setAuthUser] = useState<User | null>(user)

  const handleLogin = useCallback(() => {
    login()
  }, [login])

  const handleLogout = useCallback(() => {
    setAuthUser(null)
    logout()
  }, [logout])

  const value: AuthContextValue = {
    user: user ?? authUser,
    token,
    loading,
    error,
    isAuthenticated: !!token,
    login: handleLogin,
    logout: handleLogout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider')
  }
  return context
}
