import { useState, useCallback } from 'react'
import { useApi } from '@/hooks/useApi'
import { getRevenueAnalytics, getExpenseAnalytics, getClientAnalytics } from '@/api/analytics'
import { ChartRevenue } from '@/components/ChartRevenue'
import { ChartExpenses } from '@/components/ChartExpenses'
import { ChartClients } from '@/components/ChartClients'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { BarChart3 } from 'lucide-react'

type Period = 'month' | 'quarter' | 'year'

const periodLabels: Record<Period, string> = {
  month: 'Месяц',
  quarter: 'Квартал',
  year: 'Год',
}

export default function Analytics(): JSX.Element {
  const [period, setPeriod] = useState<Period>('month')

  const fetchRevenue = useCallback(() => getRevenueAnalytics(period), [period])
  const fetchExpenses = useCallback(() => getExpenseAnalytics(period), [period])
  const fetchClients = useCallback(() => getClientAnalytics(period), [period])

  const revenue = useApi(fetchRevenue)
  const expenses = useApi(fetchExpenses)
  const clients = useApi(fetchClients)

  const isLoading = revenue.loading || expenses.loading || clients.loading
  const hasError = revenue.error || expenses.error || clients.error

  if (isLoading) return <LoadingSpinner />
  if (hasError) return <div className="p-4 text-center text-rose-500 text-sm">{hasError}</div>
  if (!revenue.data && !expenses.data && !clients.data) return <EmptyState title="Нет данных" description="Аналитика недоступна" icon={<BarChart3 className="w-10 h-10" />} />

  const revenueChartData = revenue.data?.periods.map((p) => ({
    date: p.period,
    amount: parseFloat(p.revenue),
  })) || []

  const expenseChartData = expenses.data?.categories.map((c) => ({
    category: c.category,
    amount: parseFloat(c.amount),
  })) || []

  const clientChartData = clients.data?.periods.map((p) => ({
    period: p.period,
    new_clients: p.new_clients,
    repeat_clients: p.repeat_clients,
  })) || []

  return (
    <div className="px-4 py-4 space-y-6">
      <h1 className="text-lg font-bold">📈 Аналитика</h1>

      <div className="flex gap-2">
        {(Object.keys(periodLabels) as Period[]).map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`flex-1 py-2 rounded-xl text-sm font-medium transition-colors ${
              period === p
                ? 'bg-tg-button text-tg-buttonText'
                : 'bg-tg-secondaryBg text-tg-text'
            }`}
          >
            {periodLabels[p]}
          </button>
        ))}
      </div>

      {revenueChartData.length > 0 && (
        <div className="bg-tg-secondaryBg rounded-2xl p-4">
          <h2 className="text-sm font-semibold mb-3">Выручка</h2>
          <ChartRevenue data={revenueChartData} />
        </div>
      )}

      {expenseChartData.length > 0 && (
        <div className="bg-tg-secondaryBg rounded-2xl p-4">
          <h2 className="text-sm font-semibold mb-3">Расходы по категориям</h2>
          <ChartExpenses data={expenseChartData} />
        </div>
      )}

      {clientChartData.length > 0 && (
        <div className="bg-tg-secondaryBg rounded-2xl p-4">
          <h2 className="text-sm font-semibold mb-3">Клиенты</h2>
          <ChartClients data={clientChartData} />
        </div>
      )}
    </div>
  )
}
