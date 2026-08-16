import { NavLink, Route, Routes } from 'react-router-dom'
import { LoadingState } from './components/LoadingState'

const navigation = ['Dashboard', 'Projects', 'Settings', 'Users']

function PlaceholderPage({ title }: { title: string }) {
  return <section><h1 className="text-3xl font-semibold">{title}</h1><p className="mt-3 text-slate-400">This workspace will be available in an upcoming sprint.</p><div className="mt-6"><LoadingState label="Preparing workspace foundation…" /></div></section>
}

export default function App() {
  return <div className="min-h-screen bg-slate-950 text-slate-100"><header className="border-b border-slate-800 px-6 py-5"><p className="text-xl font-semibold tracking-tight">AI Animation Studio</p></header><div className="flex"><nav className="min-h-[calc(100vh-73px)] w-56 border-r border-slate-800 p-4" aria-label="Main navigation"><ul className="space-y-1">{navigation.map((item) => <li key={item}><NavLink className={({ isActive }) => `block rounded-md px-3 py-2 text-sm ${isActive ? 'bg-indigo-500 text-white' : 'text-slate-300 hover:bg-slate-800'}`} to={item === 'Dashboard' ? '/' : `/${item.toLowerCase()}`}>{item}</NavLink></li>)}</ul></nav><main className="p-8"><Routes><Route path="/" element={<PlaceholderPage title="Dashboard" />} /><Route path="/projects" element={<PlaceholderPage title="Projects" />} /><Route path="/settings" element={<PlaceholderPage title="Settings" />} /><Route path="/users" element={<PlaceholderPage title="Users" />} /></Routes></main></div></div>
}
