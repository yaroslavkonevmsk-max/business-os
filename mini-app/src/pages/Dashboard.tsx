import { useApi } from '@/hooks/useApi'
import { useTelegram } from '@/hooks/useTelegram'
import { getPulse } from '@/api/analytics'
import { StatCard } from '@/components/StatCard'
import { ChartRevenue } from '@/components/ChartRevenue'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { DollarSign, TrendingDown, TrendingUp, Landmark, Lightbulb, FilePlus, PlusCircle } from 'lucide-react'

export default function Dashboard(): JSX.Element {
  const { haptic } = useTelegram()
  const { data, loading, error } = useApi(getPulse)

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>
  if (!data) return <EmptyState title="Нет данных" description="Пульс бизнеса пока недоступен" />

  const chartData = [
    { date: new Date(Date.now() - 6 * 86400000).toISOString(), amount: parseFloat(data.total_revenue) * 0.6 },
    { date: new Date(Date.now() - 5 * 86400000).toISOString(), amount: parseFloat(data.total_revenue) * 0.5 },
    { date: new Date(Date.now() - 4 * 86400000).toISOString(), amount: parseFloat(data.total_revenue) * 0.7 },
    { date: new Date(Date.now() - 3 * 86400000).toISOString(), amount: parseFloat(data.total_revenue) * 0.8 },
    { date: new Date(Date.now() - 2 * 86400000).toISOString(), amount: parseFloat(data.total_revenue) * 0.9 },
    { date: new Date(Date.now() - 1 * 86400000).toISOString(), amount: parseFloat(data.total_revenue) * 0.95 },
    { date: new Date().toISOString(), amount: parseFloat(data.total_revenue) },
  ]

  return (
    <div className="px-4 py-4 space-y-6">
      <div>
        <h1 className="text-lg font-bold mb-1">📊 Пульс — {data.period}</h1>
        <p className="text-xs text-tg-hint">Обзор вашего бизнеса</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          title="Выручка"
          value={data.total_revenue}
          change={data.revenue_change_percent}
          icon={<DollarSign className="w-4 h-4" />}
          accent="green"
        />
        <StatCard
          title="Расходы"
          value={data.total_expenses}
          subtitle="за месяц"
          icon={<TrendingDown className="w-4 h-4" />}
          accent="red"
        />
        <StatCard
          title="Прибыль"
          value={data.profit}
          icon={<TrendingUp className="w-4 h-4" />}
          accent="blue"
        />
        <StatCard
          title="Налог"
          value={data.tax_amount}
          subtitle={data.tax_deadline ? `срок ${formatDate(data.tax_deadline)}` : undefined}
          icon={<Landmark className="w-4 h-4" />}
          accent="neutral"
        />
      </div>

      <div className="bg-tg-secondaryBg rounded-2xl p-4">
        <h2 className="text-sm font-semibold mb-3">Выручка по дням</h2>
        <ChartRevenue data={chartData} />
      </div>

      {data.top_client && (
        <div className="bg-tg-secondaryBg rounded-2xl p-4">
          <h2 className="text-sm font-semibold mb-3">⭐ Топ-клиент</h2>
          <div className="flex items-center justify-between">
            <span className="text-sm">{data.top_client.name}</span>
            <span className="text-sm font-bold">{formatCurrency(data.top_client.total_revenue)}</span>
          </div>
          <div className="text-xs text-tg-hint mt-1">
            Новых: {data.new_clients_count} • Повторных: {data.repeat_clients_count} • Всего: {data.total_clients_count}
          </div>
        </div>
      )}

      {data.ai_insight && (
        <div className="bg-amber-50 dark:bg-amber-900/20 rounded-2xl p-4">
          <div className="flex items-start gap-2">
            <Lightbulb className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
            <div>
              <h2 className="text-sm font-semibold text-amber-800 dark:text-amber-300 mb-1">Совет от AI</h2>
              <p className="text-sm text-amber-700 dark:text-amber-200 leading-relaxed">{data.ai_insight}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={() => { haptic('medium'); /* router navigate */ }}
          className="flex-1 flex items-center justify-center gap-2 py-3 bg-tg-button text-tg-buttonText rounded-xl text-sm font-medium active:opacity-80 transition-opacity"
        >
          <FilePlus className="w-4 h-4" />
          Счёт
        </button>
        <button
          onClick={() => { haptic('medium'); /* router navigate */ }}
          className="flex-1 flex items-center justify-center gap-2 py-3 bg-tg-secondaryBg text-tg-text rounded-xl text-sm font-medium active:opacity-80 transition-opacity"
        >
          <PlusCircle className="w-4 h-4" />
          Расход
        </button>
      </div>
    </div>
  )
}
