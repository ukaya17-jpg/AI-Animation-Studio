import { useEffect, useRef, useState, type MouseEvent } from 'react'
import {
  downloadRenderedEpisode,
  fetchRenderStatus,
  startEpisodeRender,
  toFriendlyRenderErrorMessage,
} from '../../lib/episodesApi'

type RenderButtonProps = { episodeId: string; themeId: string; className?: string }

// Only "paylasma" has real per-scene narration audio rendered so far (see
// backend/app/static/episodes/<theme_id>/sesler/) — every other theme's render
// request would 409 immediately, so this stays disabled client-side too rather
// than let someone click into a guaranteed failure.
const _AUDIO_AVAILABLE_THEME_IDS = new Set(['paylasma'])

const _POLL_INTERVAL_MS = 3000

type Phase = 'idle' | 'rendering' | 'completed' | 'failed'

/** Downloads the rendered MP4 via a synthetic, throwaway <a download> — same
 * pattern as ExportButton's ZIP download. */
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

export function RenderButton({ episodeId, themeId, className }: RenderButtonProps) {
  const [phase, setPhase] = useState<Phase>('idle')
  const [renderId, setRenderId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [downloading, setDownloading] = useState(false)
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null)

  const audioAvailable = _AUDIO_AVAILABLE_THEME_IDS.has(themeId)

  useEffect(() => {
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current)
    }
  }, [])

  function stopPolling() {
    if (pollTimer.current) {
      clearInterval(pollTimer.current)
      pollTimer.current = null
    }
  }

  async function poll(currentRenderId: string) {
    try {
      const status = await fetchRenderStatus(episodeId, currentRenderId)
      if (status.status === 'completed') {
        stopPolling()
        setPhase('completed')
      } else if (status.status === 'failed') {
        stopPolling()
        setError(status.error ?? 'Video oluşturulurken bir hata oluştu.')
        setPhase('failed')
      }
    } catch (pollError) {
      stopPolling()
      setError(toFriendlyRenderErrorMessage(pollError))
      setPhase('failed')
    }
  }

  async function handleStart(event: MouseEvent) {
    event.stopPropagation()
    setPhase('rendering')
    setError(null)
    try {
      const newRenderId = await startEpisodeRender(episodeId)
      setRenderId(newRenderId)
      pollTimer.current = setInterval(() => void poll(newRenderId), _POLL_INTERVAL_MS)
    } catch (startError) {
      setError(toFriendlyRenderErrorMessage(startError))
      setPhase('failed')
    }
  }

  async function handleDownload(event: MouseEvent) {
    event.stopPropagation()
    if (!renderId) return
    setDownloading(true)
    setError(null)
    try {
      const { blob, filename } = await downloadRenderedEpisode(episodeId, renderId)
      triggerBrowserDownload(blob, filename)
    } catch (downloadError) {
      setError(toFriendlyRenderErrorMessage(downloadError))
    } finally {
      setDownloading(false)
    }
  }

  function handleRetry(event: MouseEvent) {
    event.stopPropagation()
    setPhase('idle')
    setRenderId(null)
    setError(null)
  }

  if (!audioAvailable) {
    return (
      <div className={className}>
        <button
          type="button"
          disabled
          title="Bu bölüm için henüz tam seslendirme üretilmedi."
          className="shrink-0 cursor-not-allowed rounded-md border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-600"
        >
          🎬 Videoyu Oluştur
        </button>
      </div>
    )
  }

  return (
    <div className={className}>
      {phase === 'idle' && (
        <button
          type="button"
          onClick={(event) => void handleStart(event)}
          className="shrink-0 rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700"
        >
          🎬 Videoyu Oluştur
        </button>
      )}
      {phase === 'rendering' && (
        <button
          type="button"
          disabled
          className="shrink-0 cursor-not-allowed rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-400"
        >
          Video oluşturuluyor… (birkaç dakika sürebilir)
        </button>
      )}
      {phase === 'completed' && (
        <button
          type="button"
          onClick={(event) => void handleDownload(event)}
          disabled={downloading}
          className="shrink-0 rounded-md border border-emerald-700 bg-emerald-900/40 px-3 py-1.5 text-xs font-medium text-emerald-200 transition hover:bg-emerald-900/70 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {downloading ? 'İndiriliyor…' : '⬇️ Videoyu İndir'}
        </button>
      )}
      {phase === 'failed' && (
        <button
          type="button"
          onClick={handleRetry}
          className="shrink-0 rounded-md border border-rose-700 bg-rose-900/30 px-3 py-1.5 text-xs font-medium text-rose-200 transition hover:bg-rose-900/50"
        >
          Tekrar dene
        </button>
      )}
      {error && <p className="mt-1 text-xs text-rose-300">{error}</p>}
    </div>
  )
}
