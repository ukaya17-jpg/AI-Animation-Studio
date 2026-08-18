import axios from 'axios'
import { apiClient } from './api'
import { toFriendlyErrorMessage as toFriendlyErrorMessageGeneric } from './errors'
import type {
  EpisodeGenerationResult,
  GeneratedEpisodeList,
  ThemeSummary,
} from '../types/episode'

export async function fetchThemes(): Promise<ThemeSummary[]> {
  const response = await apiClient.get<ThemeSummary[]>('/episodes/themes')
  return response.data
}

export async function generateEpisode(
  themeId: string,
  projectId?: string,
): Promise<EpisodeGenerationResult> {
  const response = await apiClient.post<EpisodeGenerationResult>('/episodes/generate', {
    theme_id: themeId,
    project_id: projectId,
  })
  return response.data
}

export async function fetchGeneratedEpisodes(
  page = 1,
  pageSize = 20,
  projectId?: string,
): Promise<GeneratedEpisodeList> {
  const response = await apiClient.get<GeneratedEpisodeList>('/episodes', {
    params: { page, page_size: pageSize, project_id: projectId },
  })
  return response.data
}

export async function fetchGeneratedEpisode(id: string): Promise<EpisodeGenerationResult> {
  const response = await apiClient.get<EpisodeGenerationResult>(`/episodes/${id}`)
  return response.data
}

export function toFriendlyErrorMessage(error: unknown): string {
  return toFriendlyErrorMessageGeneric(error, {
    notFoundMessage: 'Seçilen tema bulunamadı.',
    fallbackMessage: 'Bölüm üretilirken beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.',
  })
}

const _FILENAME_FROM_DISPOSITION = /filename="([^"]+)"/

export async function exportEpisode(id: string): Promise<{ blob: Blob; filename: string }> {
  const response = await apiClient.get<Blob>(`/episodes/${id}/export`, { responseType: 'blob' })
  const disposition = response.headers['content-disposition'] as string | undefined
  const filename = disposition?.match(_FILENAME_FROM_DISPOSITION)?.[1] ?? 'bolum-produksiyon-paketi.zip'
  return { blob: response.data, filename }
}

/** Separate from {@link toFriendlyErrorMessage}: with `responseType: 'blob'`, a JSON error
 * body also arrives as an (unparsed) Blob, so the shared `detail`-extraction logic can't
 * read it — this reads the HTTP status directly instead. */
export function toFriendlyExportErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 404) {
      return 'Bu bölüm artık mevcut değil.'
    }
    if (error.response?.status === 401 || error.response?.status === 403) {
      return 'Bu bölümün prodüksiyon paketini indirmek için projenin sahibi olarak giriş yapmalısın.'
    }
    if (error.code === 'ECONNABORTED' || !error.response) {
      return 'Sunucuya ulaşılamadı. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.'
    }
  }
  return 'Prodüksiyon paketi indirilirken beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.'
}
