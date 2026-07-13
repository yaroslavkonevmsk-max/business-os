import { Suspense } from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Navigation } from './Navigation'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorBoundary } from './ErrorBoundary'

export function Layout(): JSX.Element {
  return (
    <div className="flex flex-col min-h-screen bg-tg-bg text-tg-text">
      <Header />
      <main className="flex-1 pb-20">
        <ErrorBoundary>
          <Suspense fallback={<LoadingSpinner />}>
            <Outlet />
          </Suspense>
        </ErrorBoundary>
      </main>
      <Navigation />
    </div>
  )
}
