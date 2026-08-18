import type { Episode } from '../../types/episode'
import { LocationMedia } from './LocationMedia'
import { VoiceSampleButton } from './VoiceSampleButton'

type EpisodeSummaryProps = { episode: Episode }

export function EpisodeSummary({ episode }: EpisodeSummaryProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-xs font-semibold uppercase tracking-wide text-indigo-300">
        {episode.theme_label}
      </p>
      <h2 className="mt-1 text-2xl font-semibold text-slate-100">{episode.title}</h2>
      <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex items-center gap-3">
          <img
            src={episode.lead_character.image_url}
            alt={episode.lead_character.name}
            className="h-12 w-12 shrink-0 rounded-full border border-slate-700 object-cover"
          />
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-500">Ana Karakter</dt>
            <dd className="mt-1 flex items-center gap-2 text-sm font-medium text-slate-200">
              <span>
                {episode.lead_character.name} ({episode.lead_character.species})
              </span>
              <VoiceSampleButton
                src={episode.lead_character.voice_sample_url}
                characterName={episode.lead_character.name}
              />
            </dd>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <img
            src={episode.support_character.image_url}
            alt={episode.support_character.name}
            className="h-12 w-12 shrink-0 rounded-full border border-slate-700 object-cover"
          />
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-500">Destek Karakter</dt>
            <dd className="mt-1 flex items-center gap-2 text-sm font-medium text-slate-200">
              <span>
                {episode.support_character.name} ({episode.support_character.species})
              </span>
              <VoiceSampleButton
                src={episode.support_character.voice_sample_url}
                characterName={episode.support_character.name}
              />
            </dd>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <LocationMedia
            videoSrc={episode.location.ambient_video_url}
            imageSrc={episode.location.image_url}
            alt={episode.location.name}
            className="h-12 w-16 shrink-0 rounded-md border border-slate-700 object-cover"
          />
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-500">Mekan</dt>
            <dd className="mt-1 text-sm font-medium text-slate-200">{episode.location.name}</dd>
          </div>
        </div>
      </dl>
      <p className="mt-4 text-xs text-slate-500">
        Toplam süre: ~{Math.round(episode.total_duration_seconds / 60)} dk (
        {episode.total_duration_seconds} sn)
      </p>
    </div>
  )
}
