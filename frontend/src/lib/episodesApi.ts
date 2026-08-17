import axios from 'axios'
import { apiClient } from './api'
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
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (error.response?.status === 404) {
      return 'Seçilen tema bulunamadı.'
    }
    if (error.code === 'ECONNABORTED' || !error.response) {
      return 'Sunucuya ulaşılamadı. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.'
    }
  }
  return 'Bölüm üretilirken beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.'
}
