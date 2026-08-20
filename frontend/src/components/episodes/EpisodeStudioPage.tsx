import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { LoadingState } from '../LoadingState'
import { EpisodeHistoryList } from './EpisodeHistoryList'
import { EpisodeSummary } from './EpisodeSummary'
import { ExportButton } from './ExportButton'
import { LessonBox } from './LessonBox'
import { RenderButton } from './RenderButton'
import { SceneCard } from './SceneCard'
import { SeoPanel } from './SeoPanel'
import { ShortsPanel } from './ShortsPanel'
import { useAuth } from '../../lib/useAuth'
import {
  fetchGeneratedEpisode,
  fetchGeneratedEpisodes,
  fetchThemes,
  generateEpisode,
  toFriendlyErrorMessage,
} from '../../lib/episodesApi'
import { fetchProjects, type Project } from '../../lib/projectsApi'
import type { EpisodeGenerationResult, GeneratedEpisodeSummary, ThemeSummary } from '../../types/episode'
import { ThemePicker } from './ThemePicker'

export function EpisodeStudioPage() {
  const { isAuthenticated } = useAuth()
  const [defaultProject, setDefaultProject] = useState<Project | null>(null)
  const [saveToProject, setSaveToProject] = useState(false)

  const [themes, setThemes] = useState<ThemeSummary[]>([])
  const [themesLoading, setThemesLoading] = useState(true)
  const [themesError, setThemesError] = useState<string | null>(null)
  const [selectedThemeId, setSelectedThemeId] = useState<string | null>(null)

  const [history, setHistory] = useState<GeneratedEpisodeSummary[]>([])
  const [historyLoading, setHistoryLoading] = useState(true)
  const [historyError, setHistoryError] = useState<string | null>(null)
  const [selectedEpisodeId, setSelectedEpisodeId] = useState<string | null>(null)

  const [result, setResult] = useState<EpisodeGenerationResult | null>(null)
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true)
    setHistoryError(null)
    try {
      const data = await fetchGeneratedEpisodes(1, 100)
      setHistory(data.items)
    } catch {
      setHistoryError('Geçmiş bölümler yüklenirken bir hata oluştu.')
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    setThemesLoading(true)
    fetchThemes()
      .then((data) => {
        if (cancelled) return
        setThemes(data)
        setSelectedThemeId((current) => current ?? data[0]?.theme_id ?? null)
      })
      .catch((error: unknown) => {
        if (!cancelled) setThemesError(toFriendlyErrorMessage(error))
      })
      .finally(() => {
        if (!cancelled) setThemesLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    void loadHistory()
  }, [loadHistory])

  useEffect(() => {
    if (!isAuthenticated) {
      setDefaultProject(null)
      setSaveToProject(false)
      return
    }
    let cancelled = false
    fetchProjects()
      .then((projects) => {
        if (!cancelled) setDefaultProject(projects[0] ?? null)
      })
      .catch(() => {
        if (!cancelled) setDefaultProject(null)
      })
    return () => {
      cancelled = true
    }
  }, [isAuthenticated])

  async function handleGenerate() {
    if (!selectedThemeId) return
    setGenerating(true)
    setGenerateError(null)
    try {
      const projectId = saveToProject && defaultProject ? defaultProject.id : undefined
      const data = await generateEpisode(selectedThemeId, projectId)
      setResult(data)
      setSelectedEpisodeId(data.id)
      await loadHistory()
    } catch (error) {
      setGenerateError(toFriendlyErrorMessage(error))
      setResult(null)
    } finally {
      setGenerating(false)
    }
  }

  async function handleSelectHistoryEpisode(episodeId: string) {
    setSelectedEpisodeId(episodeId)
    setGenerateError(null)
    setGenerating(true)
    try {
      const data = await fetchGeneratedEpisode(episodeId)
      setResult(data)
    } catch (error) {
      setGenerateError(toFriendlyErrorMessage(error))
    } finally {
      setGenerating(false)
    }
  }

  return (
    <section>
      <h1 className="text-3xl font-semibold">Neşeli Orman Bölüm Stüdyosu</h1>
      <p className="mt-2 max-w-2xl text-slate-400">
        Bir tema seç, "Bölüm Üret" butonuna bas; senaryo, YouTube SEO paketi ve Shorts kurgu planı
        saniyeler içinde hazır olsun.
      </p>

      <div className="mt-8">
        {themesLoading && <LoadingState label="Temalar yükleniyor…" />}
        {themesError && (
          <p className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
            {themesError}
          </p>
        )}
        {!themesLoading && !themesError && (
          <ThemePicker themes={themes} selectedThemeId={selectedThemeId} onSelect={setSelectedThemeId} />
        )}
      </div>

      {isAuthenticated && (
        <div className="mt-4">
          {defaultProject ? (
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={saveToProject}
                onChange={(event) => setSaveToProject(event.target.checked)}
                className="h-4 w-4 rounded border-slate-600 bg-slate-900 text-indigo-500 focus:ring-indigo-400"
              />
              Bu bölümü projeme kaydet ({defaultProject.name})
            </label>
          ) : (
            <p className="text-sm text-slate-500">
              Bölümü bir projeye kaydetmek için önce{' '}
              <Link to="/projects" className="text-indigo-300 hover:underline">
                bir proje oluştur
              </Link>
              .
            </p>
          )}
        </div>
      )}

      <div className="mt-6">
        <button
          type="button"
          onClick={handleGenerate}
          disabled={!selectedThemeId || generating}
          className="rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {generating ? 'Bölüm üretiliyor…' : 'Bölüm Üret'}
        </button>
      </div>

      {generating && (
        <div className="mt-6">
          <LoadingState label="Senaryo, SEO paketi ve Shorts planı hazırlanıyor…" />
        </div>
      )}

      {generateError && (
        <p className="mt-6 rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {generateError}
        </p>
      )}

      {result && !generating && (
        <div className="mt-8 space-y-8">
          <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <EpisodeSummary episode={result.episode} />
            </div>
            <ExportButton episodeId={result.id} className="shrink-0" />
            <RenderButton episodeId={result.id} themeId={result.episode.theme_id} className="shrink-0" />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-slate-100">Sahneler</h2>
            <div className="mt-4 space-y-4">
              {result.episode.scenes.map((scene) => (
                <SceneCard
                  key={scene.name}
                  scene={scene}
                  locationName={result.episode.location.name}
                  isInteractive={scene.name === 'Keşif'}
                />
              ))}
            </div>
          </div>

          <LessonBox lesson={result.episode.lesson} />

          <div className="space-y-4">
            <SeoPanel seo={result.seo} />
            <ShortsPanel shorts={result.shorts} />
          </div>
        </div>
      )}

      <div className="mt-12">
        <h2 className="text-xl font-semibold text-slate-100">Geçmiş Bölümler</h2>
        <p className="mt-1 text-sm text-slate-400">
          Daha önce ürettiğin bölümler burada listelenir; birine tıklayarak tekrar açabilirsin.
        </p>
        <div className="mt-4">
          {historyLoading && <LoadingState label="Geçmiş bölümler yükleniyor…" />}
          {historyError && (
            <p className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
              {historyError}
            </p>
          )}
          {!historyLoading && !historyError && (
            <EpisodeHistoryList
              episodes={history}
              selectedEpisodeId={selectedEpisodeId}
              onSelect={(episodeId) => void handleSelectHistoryEpisode(episodeId)}
            />
          )}
        </div>
      </div>
    </section>
  )
}
