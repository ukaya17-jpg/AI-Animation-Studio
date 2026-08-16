type LessonBoxProps = { lesson: string }

export function LessonBox({ lesson }: LessonBoxProps) {
  return (
    <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-emerald-300">
        Günün Dersi
      </p>
      <p className="mt-2 text-base font-medium text-emerald-50">{lesson}</p>
    </div>
  )
}
