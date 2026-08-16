import type { EpisodeScene } from '../../types/episode'

const SCENE_META: Record<string, { icon: string; badgeClass: string }> = {
  Açılış: { icon: '🎬', badgeClass: 'bg-slate-800 text-slate-300' },
  Sorun: { icon: '⚠️', badgeClass: 'bg-rose-500/10 text-rose-300' },
  Keşif: { icon: '🙋', badgeClass: 'bg-amber-500/10 text-amber-300' },
  Çözüm: { icon: '🤝', badgeClass: 'bg-emerald-500/10 text-emerald-300' },
  Kapanış: { icon: '✅', badgeClass: 'bg-indigo-500/10 text-indigo-300' },
}

const DEFAULT_SCENE_META = { icon: '🎞️', badgeClass: 'bg-slate-800 text-slate-300' }

type SceneCardProps = {
  scene: EpisodeScene
  locationName: string
  isInteractive: boolean
}

export function SceneCard({ scene, locationName, isInteractive }: SceneCardProps) {
  const meta = SCENE_META[scene.name] ?? DEFAULT_SCENE_META

  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span
            className={`flex h-8 w-8 items-center justify-center rounded-full text-base ${meta.badgeClass}`}
            aria-hidden="true"
          >
            {meta.icon}
          </span>
          <h3 className="text-lg font-semibold text-slate-100">{scene.name}</h3>
        </div>
        <div className="flex items-center gap-2">
          {isInteractive && (
            <span className="rounded-full bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-300">
              🙋 Etkileşim Anı
            </span>
          )}
          <span className="text-xs text-slate-500">{scene.duration_seconds} sn</span>
        </div>
      </div>
      <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{locationName}</p>
      <p className="mt-3 text-sm leading-relaxed text-slate-300">{scene.text}</p>
      {scene.dialogue && (
        <div className="mt-3 rounded-lg border border-slate-700 bg-slate-800/60 p-3">
          <p className="text-xs font-semibold text-indigo-300">{scene.speaker}</p>
          <p className="mt-1 text-sm italic text-slate-200">{`"${scene.dialogue}"`}</p>
        </div>
      )}
    </article>
  )
}
