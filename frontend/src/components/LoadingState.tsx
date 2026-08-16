type LoadingStateProps = { label?: string }

export function LoadingState({ label = 'Loading workspace…' }: LoadingStateProps) {
  return <div className="flex items-center gap-3 text-slate-400" role="status"><span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent" aria-hidden="true" />{label}</div>
}
