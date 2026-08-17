import axios from 'axios'

/** Best-effort extraction of a FastAPI/pydantic validation error's first message. */
function firstValidationMessage(detail: unknown): string | null {
  if (!Array.isArray(detail) || detail.length === 0) return null
  const first = detail[0] as { msg?: unknown }
  return typeof first?.msg === 'string' ? first.msg : null
}

type FriendlyErrorOptions = {
  /** Shown for a 404 with no string `detail` (e.g. a picked-from-a-list resource). */
  notFoundMessage?: string
  /** Shown when nothing more specific could be extracted from the response. */
  fallbackMessage: string
}

export function toFriendlyErrorMessage(error: unknown, options: FriendlyErrorOptions): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail
    if (typeof detail === 'string') {
      return detail
    }
    const validationMessage = firstValidationMessage(detail)
    if (validationMessage) {
      return validationMessage
    }
    if (options.notFoundMessage && error.response?.status === 404) {
      return options.notFoundMessage
    }
    if (error.code === 'ECONNABORTED' || !error.response) {
      return 'Sunucuya ulaşılamadı. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.'
    }
  }
  return options.fallbackMessage
}
