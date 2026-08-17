import { apiClient } from './api'

export type AuthUser = {
  id: string
  email: string
  created_at: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export async function registerAccount(email: string, password: string): Promise<AuthUser> {
  const response = await apiClient.post<AuthUser>('/auth/register', { email, password })
  return response.data
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', { email, password })
  return response.data
}
