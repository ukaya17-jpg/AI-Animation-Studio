import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { login as loginRequest, registerAccount } from './authApi'
import { setAccessToken } from './api'
import { AuthContext, type AuthContextValue } from './authContextValue'

// Storing the access token in localStorage (rather than an httpOnly cookie) means
// any script that runs in this origin — including one injected via an XSS bug —
// can read it. Acceptable for this stage (no refresh tokens, 60-minute expiry,
// no sensitive PII beyond email), but a production hardening pass should move
// this to an httpOnly cookie set by the backend.
const TOKEN_STORAGE_KEY = 'aas_access_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_STORAGE_KEY))

  useEffect(() => {
    setAccessToken(token)
  }, [token])

  const persistToken = useCallback((next: string | null) => {
    setToken(next)
    if (next) {
      localStorage.setItem(TOKEN_STORAGE_KEY, next)
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await loginRequest(email, password)
      persistToken(access_token)
    },
    [persistToken],
  )

  const register = useCallback(
    async (email: string, password: string) => {
      await registerAccount(email, password)
      await login(email, password)
    },
    [login],
  )

  const logout = useCallback(() => {
    persistToken(null)
  }, [persistToken])

  const value = useMemo<AuthContextValue>(
    () => ({ token, isAuthenticated: token !== null, login, register, logout }),
    [token, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
