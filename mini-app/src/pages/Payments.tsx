import { useApi } from '@/hooks/useApi'
import { getPayments } from '@/api/payments'
import { PaymentRow } from '@/components/PaymentRow'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { Wallet } from 'lucide-react'

export default function Payments(): JSX.Element {
  const { data, loading, error } = useApi(() => getPayments(1))

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>
  if (!data || data.items.length === 0) return <EmptyState title="Нет платежей" description="История платежей пуста" icon={<Wallet className="w-10 h-10" />} />

  return (
    <div className="px-4 py-4 space-y-4">
      <h1 className="text-lg font-bold">💰 Платежи</h1>
      <div className="space-y-2">
        {data.items.map((payment) => (
          <PaymentRow key={payment.id} payment={payment} />
        ))}
      </div>
    </div>
  )
}
