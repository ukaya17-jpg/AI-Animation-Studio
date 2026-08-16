import type { SeoPackage } from '../../types/episode'
import { CopyButton } from './CopyButton'

type SeoPanelProps = { seo: SeoPackage }

export function SeoPanel({ seo }: SeoPanelProps) {
  return (
    <details className="group rounded-xl border border-slate-800 bg-slate-900" open>
      <summary className="cursor-pointer list-none px-5 py-4 text-base font-semibold text-slate-100 marker:content-none">
        <span className="flex items-center justify-between">
          YouTube SEO Paketi
          <span className="text-sm text-slate-500 transition group-open:rotate-180" aria-hidden="true">
            ▾
          </span>
        </span>
      </summary>
      <div className="space-y-5 border-t border-slate-800 px-5 py-5">
        <div>
          <p className="text-sm font-semibold text-slate-300">Başlık Seçenekleri</p>
          <ul className="mt-2 space-y-2">
            {seo.titles.map((title, index) => (
              <li
                key={index}
                className="flex items-center justify-between gap-3 rounded-lg bg-slate-800/60 px-3 py-2 text-sm text-slate-200"
              >
                <span>{title}</span>
                <CopyButton value={title} />
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-300">Açıklama</p>
            <CopyButton value={seo.description} />
          </div>
          <pre className="mt-2 whitespace-pre-wrap rounded-lg bg-slate-800/60 p-3 font-sans text-sm text-slate-200">
            {seo.description}
          </pre>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-300">Etiketler</p>
            <CopyButton value={seo.tags.join(', ')} />
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {seo.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-300"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div>
          <p className="text-sm font-semibold text-slate-300">Thumbnail Önerisi</p>
          <p className="mt-2 text-sm text-slate-300">{seo.thumbnail_suggestion}</p>
        </div>
      </div>
    </details>
  )
}
