export type ThemeSummary = {
  theme_id: string
  label: string
  lead_character_image_url: string
  support_character_image_url: string
  location_image_url: string
}

export type VoiceProfile = {
  pitch: string
  pace: string
  tone: string
  catchphrase: string
}

export type EpisodeCharacter = {
  character_id: string
  name: string
  species: string
  role: string
  core_value: string
  personality: string[]
  visual_description: string
  voice: VoiceProfile
  image_url: string
}

export type EpisodeLocation = {
  location_id: string
  name: string
  type: string
  description: string
  image_url: string
}

export type EpisodeScene = {
  name: string
  duration_seconds: number
  text: string
  speaker: string | null
  dialogue: string | null
}

export type Episode = {
  theme_id: string
  theme_label: string
  title: string
  lead_character: EpisodeCharacter
  support_character: EpisodeCharacter
  location: EpisodeLocation
  lesson: string
  total_duration_seconds: number
  scenes: EpisodeScene[]
}

export type SeoPackage = {
  titles: string[]
  description: string
  tags: string[]
  thumbnail_suggestion: string
}

export type ShortsSegment = {
  name: string
  duration_seconds: number
  text: string
}

export type ShortsPlan = {
  episode_theme_id: string
  total_duration_seconds: number
  segments: ShortsSegment[]
}

export type EpisodeGenerationResult = {
  id: string
  project_id: string | null
  episode: Episode
  seo: SeoPackage
  shorts: ShortsPlan
}

export type GeneratedEpisodeSummary = {
  id: string
  project_id: string | null
  title: string
  theme_id: string
  theme_label: string
  lead_character_image_url: string
  support_character_image_url: string
  location_image_url: string
  created_at: string
}

export type GeneratedEpisodeList = {
  items: GeneratedEpisodeSummary[]
  total: number
  page: number
  page_size: number
}
