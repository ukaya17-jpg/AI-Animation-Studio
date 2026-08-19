import { useState, type MouseEvent } from 'react'

type TalkingSampleButtonProps = {
  src: string
  characterName: string
}

/**
 * Showcase button for a character's optional lip-synced talking-sample video.
 * Only rendered when a theme's character actually has one (currently just Kurnaz) —
 * see docs/ses-rehberi.md for why this hasn't been produced for the full cast yet.
 */
export function TalkingSampleButton({ src, characterName }: TalkingSampleButtonProps) {
  const [open, setOpen] = useState(false)

  function handleOpen(event: MouseEvent<HTMLButtonElement>) {
    // Stops the click from bubbling to the ancestor that selects the theme card.
    event.preventDefault()
    event.stopPropagation()
    setOpen(true)
  }

  function handleClose(event: MouseEvent) {
    event.stopPropagation()
    setOpen(false)
  }

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        className="mt-2 inline-flex items-center gap-1 rounded-full border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 text-[11px] font-normal text-amber-300 transition hover:bg-amber-500/20"
      >
        🎬 Canlandırılmış Örneği Gör
      </button>
      {open && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={`${characterName} canlandırılmış örnek videosu`}
          onClick={handleClose}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
        >
          <div
            onClick={(event) => event.stopPropagation()}
            className="w-full max-w-lg rounded-xl bg-slate-900 p-3 shadow-xl"
          >
            <video src={src} controls autoPlay className="w-full rounded-lg" />
            <button
              type="button"
              onClick={handleClose}
              className="mt-3 w-full rounded-md border border-slate-700 py-1.5 text-sm text-slate-200 transition hover:bg-slate-800"
            >
              Kapat
            </button>
          </div>
        </div>
      )}
    </>
  )
}
