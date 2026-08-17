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
