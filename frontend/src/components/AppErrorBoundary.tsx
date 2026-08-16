import { Component, type ErrorInfo, type ReactNode } from 'react'

type AppErrorBoundaryProps = { children: ReactNode }
type AppErrorBoundaryState = { hasError: boolean }

export class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  public state: AppErrorBoundaryState = { hasError: false }

  public static getDerivedStateFromError(): AppErrorBoundaryState {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Unhandled frontend error', error, errorInfo)
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return <main className="grid min-h-screen place-items-center bg-slate-950 p-6 text-slate-100"><section className="max-w-md text-center"><h1 className="text-2xl font-semibold">Something went wrong</h1><p className="mt-3 text-slate-400">Please refresh the page and try again.</p></section></main>
    }

    return this.props.children
  }
}
