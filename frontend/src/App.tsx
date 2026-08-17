import { NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import { LoadingState } from './components/LoadingState'
import { EpisodeStudioPage } from './components/episodes/EpisodeStudioPage'
import { LoginPage } from './components/auth/LoginPage'
import { RegisterPage } from './components/auth/RegisterPage'
import { ProjectsPage } from './components/projects/ProjectsPage'
import { AuthProvider } from './lib/authContext'
import { useAuth } from './lib/useAuth'

const navigation = [
  { label: 'Dashboard', path: '/' },
  { label: 'Projects', path: '/projects' },
  { label: 'Settings', path: '/settings' },
  { label: 'Users', path: '/users' },
  { label: 'Neşeli Orman', path: '/episodes' },
]

function PlaceholderPage({ title }: { title: string }) {
  return (
    <section>
      <h1 className="text-3xl font-semibold">{title}</h1>
      <p className="mt-3 text-slate-400">This workspace will be available in an upcoming sprint.</p>
      <div className="mt-6">
        <LoadingState label="Preparing workspace foundation…" />
      </div>
    </section>
  )
}

function AuthStatus() {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  if (!isAuthenticated) {
    return (
      <NavLink to="/login" className="text-sm font-medium text-indigo-300 hover:underline">
        Giriş Yap
      </NavLink>
    )
  }

  return (
    <button
      type="button"
      onClick={() => {
        logout()
        navigate('/')
      }}
      className="text-sm font-medium text-slate-300 hover:text-white"
    >
      Çıkış Yap
    </button>
  )
}

function AppShell() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="flex items-center justify-between border-b border-slate-800 px-6 py-5">
        <p className="text-xl font-semibold tracking-tight">AI Animation Studio</p>
        <AuthStatus />
      </header>
      <div className="flex flex-col md:flex-row">
        <nav
          className="border-b border-slate-800 p-2 md:min-h-[calc(100vh-73px)] md:w-56 md:border-b-0 md:border-r md:p-4"
          aria-label="Main navigation"
        >
          <ul className="flex gap-1 overflow-x-auto md:flex-col md:space-y-1 md:overflow-visible">
            {navigation.map((item) => (
              <li key={item.path} className="shrink-0">
                <NavLink
                  className={({ isActive }) =>
                    `block whitespace-nowrap rounded-md px-3 py-2 text-sm ${
                      isActive ? 'bg-indigo-500 text-white' : 'text-slate-300 hover:bg-slate-800'
                    }`
                  }
                  to={item.path}
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <main className="min-w-0 flex-1 p-4 sm:p-6 md:p-8">
          <Routes>
            <Route path="/" element={<PlaceholderPage title="Dashboard" />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
            <Route path="/users" element={<PlaceholderPage title="Users" />} />
            <Route path="/episodes" element={<EpisodeStudioPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  )
}
