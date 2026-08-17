import axios from 'axios'

export const apiClient = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? '/api', timeout: 10_000 })

let currentAccessToken: string | null = null

/** Called by AuthProvider whenever the signed-in token changes (or clears). */
export function setAccessToken(token: string | null): void {
  currentAccessToken = token
}

apiClient.interceptors.request.use((config) => {
  if (currentAccessToken) {
    config.headers.Authorization = `Bearer ${currentAccessToken}`
  }
  return config
})
