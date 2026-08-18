import { useState } from 'react'
import {
  exportEpisodesBatch,
  generateEpisodesBatch,
  toFriendlyBatchExportErrorMessage,
  toFriendlyBatchGenerateErrorMessage,
} from '../../lib/episodesApi'
import type { Project } from '../../lib/projectsApi'
import type { GeneratedEpisodeSummary } from '../../types/episode'

/** Downloads a blob via a synthetic, throwaway <a download> (same approach as ExportButton). */
function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

type ProjectCardProps = {
  project: Project
  episodes: GeneratedEpisodeSummary[]
  onEpisodesChanged: () => Promise<void>
}

export function ProjectCard({ project, episodes, onEpisodesChanged }: ProjectCardProps) {
  const [generating, setGenerating] = useState(false)
  const [generateSummary, setGenerateSummary] = useState<string | null>(null)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState<string | null>(null)

  async function handleBatchGenerate() {
    setGenerating(true)
    setGenerateError(null)
    setGenerateSummary(null)
    try {
      const result = await generateEpisodesBatch(project.id)
      setGenerateSummary(
        result.created.length === 0
          ? 'Tüm temalar zaten üretilmiş, yeni bölüm üretilmedi.'
          : `${result.created.length} yeni bölüm üretildi${
              result.skipped_theme_ids.length > 0
                ? ` (${result.skipped_theme_ids.length} tema zaten üretilmiş olduğu için atlandı)`
                : ''
            }.`,
      )
      await onEpisodesChanged()
    } catch (err) {
      setGenerateError(toFriendlyBatchGenerateErrorMessage(err))
    } finally {
      setGenerating(false)
    }
  }

  async function handleBatchDownload() {
    setDownloading(true)
    setDownloadError(null)
    try {
      const { blob, filename } = await exportEpisodesBatch(project.id)
      triggerBrowserDownload(blob, filename)
    } catch (err) {
      setDownloadError(toFriendlyBatchExportErrorMessage(err))
    } finally {
      setDownloading(false)
    }
  }

  return (
    <li className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-100">{project.name}</h2>
        <div className="flex shrink-0 flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void handleBatchGenerate()}
            disabled={generating}
            className="rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {generating ? '20 bölüm üretiliyor (biraz sürebilir)…' : '🎬 Tüm Temalarla Toplu Üret'}
          </button>
          {episodes.length > 0 && (
            <button
              type="button"
              onClick={() => void handleBatchDownload()}
              disabled={downloading}
              className="rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {downloading ? 'Paket hazırlanıyor…' : '📦 Tüm Bölümleri İndir (ZIP)'}
            </button>
          )}
        </div>
      </div>

      {generateSummary && <p className="mt-2 text-xs text-emerald-300">{generateSummary}</p>}
      {generateError && (
        <p role="alert" className="mt-2 text-xs text-rose-300">
          {generateError}
        </p>
      )}
      {downloadError && (
        <p role="alert" className="mt-2 text-xs text-rose-300">
          {downloadError}
        </p>
      )}

      {episodes.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">Bu projeye henüz bölüm kaydedilmedi.</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {episodes.map((episode) => (
            <li key={episode.id} className="text-sm text-slate-300">
              {episode.title}
            </li>
          ))}
        </ul>
      )}
    </li>
  )
}
