import type { ShortsPlan } from '../../types/episode'

const SEGMENT_LABELS: Record<string, string> = {
  hook: 'Hook',
  problem: 'Sorun',
  interaction: 'Etkileşim',
  resolution_and_lesson: 'Çözüm + Ders',
  cta: 'Abone Çağrısı',
}

type ShortsPanelProps = { shorts: ShortsPlan }

export function ShortsPanel({ shorts }: ShortsPanelProps) {
  return (
    <details className="group rounded-xl border border-slate-800 bg-slate-900">
      <summary className="cursor-pointer list-none px-5 py-4 text-base font-semibold text-slate-100 marker:content-none">
        <span className="flex items-center justify-between">
          Shorts Kurgu Planı ({shorts.total_duration_seconds} sn)
          <span className="text-sm text-slate-500 transition group-open:rotate-180" aria-hidden="true">
            ▾
          </span>
        </span>
      </summary>
      <ol className="space-y-3 border-t border-slate-800 px-5 py-5">
        {shorts.segments.map((segment, index) => (
          <li key={segment.name} className="flex gap-3 rounded-lg bg-slate-800/60 p-3">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-500/20 text-xs font-semibold text-indigo-300">
              {index + 1}
            </span>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                {SEGMENT_LABELS[segment.name] ?? segment.name} · {segment.duration_seconds} sn
              </p>
              <p className="mt-1 text-sm text-slate-200">{segment.text}</p>
            </div>
          </li>
        ))}
      </ol>
    </details>
  )
}
