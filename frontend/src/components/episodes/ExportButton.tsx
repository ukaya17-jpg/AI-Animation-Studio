import { useState, type MouseEvent } from 'react'
import { exportEpisode, toFriendlyExportErrorMessage } from '../../lib/episodesApi'

type ExportButtonProps = { episodeId: string; className?: string }

/** Downloads the episode's production package ZIP via a synthetic, throwaway <a download>. */
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

export function ExportButton({ episodeId, className }: ExportButtonProps) {
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleClick(event: MouseEvent) {
    event.stopPropagation()
    setDownloading(true)
    setError(null)
    try {
      const { blob, filename } = await exportEpisode(episodeId)
      triggerBrowserDownload(blob, filename)
    } catch (downloadError) {
      setError(toFriendlyExportErrorMessage(downloadError))
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className={className}>
      <button
        type="button"
        onClick={(event) => void handleClick(event)}
        disabled={downloading}
        className="shrink-0 rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {downloading ? 'Paket hazırlanıyor…' : '📦 Prodüksiyon Paketini İndir'}
      </button>
      {error && <p className="mt-1 text-xs text-rose-300">{error}</p>}
    </div>
  )
}
