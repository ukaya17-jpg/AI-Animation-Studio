import { useRef, useState, type MouseEvent } from 'react'

type VoiceSampleButtonProps = {
  src: string
  characterName: string
}

export function VoiceSampleButton({ src, characterName }: VoiceSampleButtonProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [playing, setPlaying] = useState(false)

  function handleClick(event: MouseEvent<HTMLButtonElement>) {
    // Stops the click from bubbling to an ancestor that selects a theme/card.
    event.preventDefault()
    event.stopPropagation()
    const audio = audioRef.current
    if (!audio) return
    if (audio.paused) {
      void audio.play()
    } else {
      audio.pause()
    }
  }

  return (
    <span className="inline-flex">
      <button
        type="button"
        onClick={handleClick}
        aria-label={`${characterName} sesini dinle`}
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-slate-700 bg-slate-800/90 text-[10px] text-slate-200 transition hover:bg-slate-700"
      >
        {playing ? '⏸' : '▶'}
      </button>
      <audio
        ref={audioRef}
        src={src}
        preload="none"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
      />
    </span>
  )
}
