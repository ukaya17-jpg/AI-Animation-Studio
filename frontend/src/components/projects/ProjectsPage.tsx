import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { LoadingState } from '../LoadingState'
import { ProjectCard } from './ProjectCard'
import { useAuth } from '../../lib/useAuth'
import { toFriendlyErrorMessage } from '../../lib/errors'
import { fetchGeneratedEpisodes } from '../../lib/episodesApi'
import { createProject, fetchProjects, type Project } from '../../lib/projectsApi'
import type { GeneratedEpisodeSummary } from '../../types/episode'

type ProjectWithEpisodes = Project & { episodes: GeneratedEpisodeSummary[] }

export function ProjectsPage() {
  const { isAuthenticated } = useAuth()
  const [projects, setProjects] = useState<ProjectWithEpisodes[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newProjectName, setNewProjectName] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  const loadProjects = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const baseProjects = await fetchProjects()
      const withEpisodes = await Promise.all(
        baseProjects.map(async (project) => {
          const episodeList = await fetchGeneratedEpisodes(1, 100, project.id)
          return { ...project, episodes: episodeList.items }
        }),
      )
      setProjects(withEpisodes)
    } catch (err) {
      setError(
        toFriendlyErrorMessage(err, { fallbackMessage: 'Projeler yüklenirken bir hata oluştu.' }),
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isAuthenticated) void loadProjects()
  }, [isAuthenticated, loadProjects])

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const name = newProjectName.trim()
    if (!name) return
    setCreating(true)
    setCreateError(null)
    try {
      await createProject(name)
      setNewProjectName('')
      await loadProjects()
    } catch (err) {
      setCreateError(
        toFriendlyErrorMessage(err, { fallbackMessage: 'Proje oluşturulurken bir hata oluştu.' }),
      )
    } finally {
      setCreating(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <section>
        <h1 className="text-3xl font-semibold">Projeler</h1>
        <p className="mt-3 text-slate-400">
          Projelerini görmek ve yönetmek için{' '}
          <Link to="/login" className="text-indigo-300 hover:underline">
            giriş yapmalısın
          </Link>
          .
        </p>
      </section>
    )
  }

  return (
    <section>
      <h1 className="text-3xl font-semibold">Projeler</h1>
      <p className="mt-2 max-w-2xl text-slate-400">
        Projelerin ve onlara kaydedilen Neşeli Orman bölümleri burada listelenir.
      </p>

      <form
        onSubmit={(event) => void handleCreateProject(event)}
        className="mt-6 flex flex-col gap-2 sm:flex-row"
      >
        <label htmlFor="new-project-name" className="sr-only">
          Yeni proje adı
        </label>
        <input
          id="new-project-name"
          type="text"
          value={newProjectName}
          onChange={(event) => setNewProjectName(event.target.value)}
          placeholder="Yeni proje adı"
          className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none"
        />
        <button
          type="submit"
          disabled={creating || !newProjectName.trim()}
          className="shrink-0 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {creating ? 'Oluşturuluyor…' : 'Proje Oluştur'}
        </button>
      </form>
      {createError && (
        <p role="alert" className="mt-2 text-sm text-rose-300">
          {createError}
        </p>
      )}

      <div className="mt-8">
        {/* Only the very first load blanks the section out; a background refresh
            triggered later (e.g. after a per-project batch action) keeps the
            existing list mounted so ProjectCard doesn't lose its own local
            state (a batch result summary, a download error, ...) mid-flight. */}
        {loading && projects.length === 0 && <LoadingState label="Projeler yükleniyor…" />}
        {error && (
          <p
            role="alert"
            className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300"
          >
            {error}
          </p>
        )}
        {!loading && !error && projects.length === 0 && (
          <p className="text-sm text-slate-400">Henüz bir proje oluşturmadın.</p>
        )}
        {projects.length > 0 && (
          <ul className="space-y-4">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                episodes={project.episodes}
                onEpisodesChanged={loadProjects}
              />
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
