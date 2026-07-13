import { Routes, Route } from 'react-router-dom'
import { lazy } from 'react'
import { AuthProvider } from '@/context/AuthContext'
import { useTheme } from '@/hooks/useTheme'
import { Layout } from '@/components/Layout'
import { LoadingSpinner } from '@/components/LoadingSpinner'

const Dashboard = lazy(() => import('@/pages/Dashboard'))
const Clients = lazy(() => import('@/pages/Clients'))
const ClientDetail = lazy(() => import('@/pages/ClientDetail'))
const Documents = lazy(() => import('@/pages/Documents'))
const DocumentDetail = lazy(() => import('@/pages/DocumentDetail'))
const Payments = lazy(() => import('@/pages/Payments'))
const Expenses = lazy(() => import('@/pages/Expenses'))
const Analytics = lazy(() => import('@/pages/Analytics'))
const Taxes = lazy(() => import('@/pages/Taxes'))
const Settings = lazy(() => import('@/pages/Settings'))
const BankConnection = lazy(() => import('@/pages/BankConnection'))

function ThemedApp(): JSX.Element {
  useTheme()
  return (
    <AuthProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/clients/:id" element={<ClientDetail />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/:id" element={<DocumentDetail />} />
          <Route path="/payments" element={<Payments />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/taxes" element={<Taxes />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/bank-connection" element={<BankConnection />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default function App(): JSX.Element {
  return (
    <div className="min-h-screen bg-tg-bg text-tg-text">
      <ThemedApp />
    </div>
  )
}
