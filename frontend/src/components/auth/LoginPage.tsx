import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/useAuth'
import { toFriendlyErrorMessage } from '../../lib/errors'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email, password)
      navigate('/projects')
    } catch (err) {
      setError(
        toFriendlyErrorMessage(err, { fallbackMessage: 'Giriş yapılırken bir hata oluştu.' }),
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="max-w-sm">
      <h1 className="text-3xl font-semibold">Giriş Yap</h1>
      <form onSubmit={(event) => void handleSubmit(event)} className="mt-6 space-y-4" noValidate>
        <div>
          <label htmlFor="login-email" className="block text-sm font-medium text-slate-300">
            E-posta
          </label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="login-password" className="block text-sm font-medium text-slate-300">
            Şifre
          </label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none"
          />
        </div>
        {error && (
          <p
            role="alert"
            className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300"
          >
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {submitting ? 'Giriş yapılıyor…' : 'Giriş Yap'}
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-400">
        Hesabın yok mu?{' '}
        <Link to="/register" className="text-indigo-300 hover:underline">
          Kayıt ol
        </Link>
      </p>
    </section>
  )
}
