import type { KeyboardEvent } from 'react'
import type { ThemeSummary } from '../../types/episode'
import { LocationMedia } from './LocationMedia'
import { VoiceSampleButton } from './VoiceSampleButton'

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

        function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            onSelect(theme.theme_id)
          }
        }

        return (
          // A <div> rather than a <button> here so the per-character "listen"
          // buttons below can be real, independently clickable <button>s —
          // nesting <button> inside <button> is invalid HTML and browsers
          // silently break its click handling.
          <div
            key={theme.theme_id}
            role="radio"
            aria-checked={isSelected}
            tabIndex={0}
            onClick={() => onSelect(theme.theme_id)}
            onKeyDown={handleKeyDown}
            className={`cursor-pointer rounded-xl border px-4 py-3 text-left text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
              isSelected
                ? 'border-indigo-400 bg-indigo-500/10 text-indigo-200'
                : 'border-slate-800 bg-slate-900 text-slate-200 hover:border-slate-700 hover:bg-slate-800'
            }`}
          >
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <div className="flex -space-x-2">
                  <img
                    src={theme.lead_character_image_url}
                    alt={theme.lead_character_name}
                    className="h-9 w-9 rounded-full border-2 border-slate-900 bg-slate-800 object-cover"
                  />
                  <img
                    src={theme.support_character_image_url}
                    alt={theme.support_character_name}
                    className="h-9 w-9 rounded-full border-2 border-slate-900 bg-slate-800 object-cover"
                  />
                </div>
                <VoiceSampleButton
                  src={theme.lead_character_voice_sample_url}
                  characterName={theme.lead_character_name}
                />
                <VoiceSampleButton
                  src={theme.support_character_voice_sample_url}
                  characterName={theme.support_character_name}
                />
              </div>
              <LocationMedia
                videoSrc={theme.location_ambient_video_url}
                imageSrc={theme.location_image_url}
                alt={theme.location_name}
                className="h-9 w-14 rounded-md border border-slate-700 object-cover"
              />
            </div>
            <p className="mt-2">{theme.label}</p>
          </div>
        )
      })}
    </div>
  )
}
