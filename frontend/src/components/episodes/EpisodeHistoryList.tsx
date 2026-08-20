import type { KeyboardEvent } from 'react'
import type { GeneratedEpisodeSummary } from '../../types/episode'
import { ExportButton } from './ExportButton'
import { RenderButton } from './RenderButton'

type EpisodeHistoryListProps = {
  episodes: GeneratedEpisodeSummary[]
  selectedEpisodeId: string | null
  onSelect: (episodeId: string) => void
}

const dateFormatter = new Intl.DateTimeFormat('tr-TR', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function EpisodeHistoryList({
  episodes,
  selectedEpisodeId,
  onSelect,
}: EpisodeHistoryListProps) {
  if (episodes.length === 0) {
    return (
      <p className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-400">
        Henüz üretilmiş bir bölüm yok. Yukarıdan bir tema seçip "Bölüm Üret" butonuna basarak
        başlayabilirsin.
      </p>
    )
  }

  return (
    <ul className="space-y-2">
      {episodes.map((episode) => {
        const isSelected = episode.id === selectedEpisodeId

        function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            onSelect(episode.id)
          }
        }

        return (
          <li key={episode.id}>
            {/* A <div> rather than a <button>, so the "export" button below can be a
                real, independently clickable <button> — nesting <button> inside
                <button> is invalid HTML (see the same note in ThemePicker.tsx). */}
            <div
              role="button"
              tabIndex={0}
              onClick={() => onSelect(episode.id)}
              onKeyDown={handleKeyDown}
              aria-current={isSelected}
              className={`flex w-full cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-left transition focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                isSelected
                  ? 'border-indigo-400 bg-indigo-500/10'
                  : 'border-slate-800 bg-slate-900 hover:border-slate-700 hover:bg-slate-800'
              }`}
            >
              <div className="flex -space-x-2">
                <img
                  src={episode.lead_character_image_url}
                  alt={episode.lead_character_name}
                  className="h-8 w-8 rounded-full border-2 border-slate-900 bg-slate-800 object-cover"
                />
                <img
                  src={episode.support_character_image_url}
                  alt={episode.support_character_name}
                  className="h-8 w-8 rounded-full border-2 border-slate-900 bg-slate-800 object-cover"
                />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-200">{episode.title}</p>
                <p className="mt-0.5 text-xs text-slate-500">
                  {episode.theme_label} · {dateFormatter.format(new Date(episode.created_at))}
                </p>
              </div>
              <ExportButton episodeId={episode.id} />
              <RenderButton episodeId={episode.id} themeId={episode.theme_id} />
            </div>
          </li>
        )
      })}
    </ul>
  )
}
