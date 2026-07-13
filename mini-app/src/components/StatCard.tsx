import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatCurrency, formatPercent } from '@/utils/formatters'

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  subtitle?: string
  icon: React.ReactNode
  accent?: 'green' | 'red' | 'blue' | 'neutral'
}

export function StatCard({ title, value, change, subtitle, icon, accent = 'blue' }: StatCardProps): JSX.Element {
  const accentClasses = {
    green: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400',
    red: 'bg-rose-50 text-rose-700 dark:bg-rose-900/20 dark:text-rose-400',
    blue: 'bg-sky-50 text-sky-700 dark:bg-sky-900/20 dark:text-sky-400',
    neutral: 'bg-gray-50 text-gray-700 dark:bg-gray-800/50 dark:text-gray-400',
  }

  const changeIcon =
    change == null ? null : change > 0 ? (
      <TrendingUp className="w-3 h-3" />
    ) : change < 0 ? (
      <TrendingDown className="w-3 h-3" />
    ) : (
      <Minus className="w-3 h-3" />
    )

  return (
    <div className={`rounded-2xl p-4 ${accentClasses[accent]}`}>
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs font-medium opacity-70">{title}</span>
        <div className="opacity-60">{icon}</div>
      </div>
      <div className="text-xl font-bold tracking-tight">{formatCurrency(value)}</div>
      <div className="flex items-center gap-1 mt-1">
        {changeIcon}
        {change != null && <span className="text-xs font-medium">{formatPercent(change)}</span>}
        {subtitle && <span className="text-xs opacity-70">{subtitle}</span>}
      </div>
    </div>
  )
}
