import { useCallback, useEffect, useState } from 'react'
import { LoadingState } from '../LoadingState'
import { EpisodeHistoryList } from './EpisodeHistoryList'
import { EpisodeSummary } from './EpisodeSummary'
import { LessonBox } from './LessonBox'
import { SceneCard } from './SceneCard'
import { SeoPanel } from './SeoPanel'
import { ShortsPanel } from './ShortsPanel'
import {
  fetchGeneratedEpisode,
  fetchGeneratedEpisodes,
  fetchThemes,
  generateEpisode,
  toFriendlyErrorMessage,
} from '../../lib/episodesApi'
import type { EpisodeGenerationResult, GeneratedEpisodeSummary, ThemeSummary } from '../../types/episode'
import { ThemePicker } from './ThemePicker'

export function EpisodeStudioPage() {
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
      const data = await fetchGeneratedEpisodes()
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

  async function handleGenerate() {
    if (!selectedThemeId) return
    setGenerating(true)
    setGenerateError(null)
    try {
      const data = await generateEpisode(selectedThemeId)
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
          <EpisodeSummary episode={result.episode} />

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
