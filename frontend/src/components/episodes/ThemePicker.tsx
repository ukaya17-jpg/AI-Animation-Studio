import type { ThemeSummary } from '../../types/episode'

type ThemePickerProps = {
  themes: ThemeSummary[]
  selectedThemeId: string | null
  onSelect: (themeId: string) => void
}

export function ThemePicker({ themes, selectedThemeId, onSelect }: ThemePickerProps) {
  return (
    <div
      className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3"
      role="radiogroup"
      aria-label="Tema seç"
    >
      {themes.map((theme) => {
        const isSelected = theme.theme_id === selectedThemeId
        return (
          <button
            key={theme.theme_id}
            type="button"
            role="radio"
            aria-checked={isSelected}
            onClick={() => onSelect(theme.theme_id)}
            className={`rounded-xl border px-4 py-3 text-left text-sm font-medium transition ${
              isSelected
                ? 'border-indigo-400 bg-indigo-500/10 text-indigo-200'
                : 'border-slate-800 bg-slate-900 text-slate-200 hover:border-slate-700 hover:bg-slate-800'
            }`}
          >
            {theme.label}
          </button>
        )
      })}
    </div>
  )
}
