import type { Episode } from '../../types/episode'

type EpisodeSummaryProps = { episode: Episode }

export function EpisodeSummary({ episode }: EpisodeSummaryProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-xs font-semibold uppercase tracking-wide text-indigo-300">
        {episode.theme_label}
      </p>
      <h2 className="mt-1 text-2xl font-semibold text-slate-100">{episode.title}</h2>
      <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Ana Karakter</dt>
          <dd className="mt-1 text-sm font-medium text-slate-200">
            {episode.lead_character.name} ({episode.lead_character.species})
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Destek Karakter</dt>
          <dd className="mt-1 text-sm font-medium text-slate-200">
            {episode.support_character.name} ({episode.support_character.species})
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Mekan</dt>
          <dd className="mt-1 text-sm font-medium text-slate-200">{episode.location.name}</dd>
        </div>
      </dl>
      <p className="mt-4 text-xs text-slate-500">
        Toplam süre: ~{Math.round(episode.total_duration_seconds / 60)} dk (
        {episode.total_duration_seconds} sn)
      </p>
    </div>
  )
}
