import { useApi } from '@/hooks/useApi'
import { getTaxes, getCurrentTax } from '@/api/taxes'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { Landmark, AlertTriangle, CheckCircle } from 'lucide-react'

const regimeLabels: Record<string, string> = {
  usn_income: 'УСН Доходы (6%)',
  usn_income_expense: 'УСН Доходы минус Расходы (15%)',
  npd: 'Налог на проф. доход (НПД)',
  patent: 'Патент',
}

export default function Taxes(): JSX.Element {
  const { data: currentTax, loading: loadingCurrent, error: errorCurrent } = useApi(getCurrentTax)
  const { data: taxes, loading: loadingAll, error: errorAll } = useApi(getTaxes)

  const loading = loadingCurrent || loadingAll
  const error = errorCurrent || errorAll

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>

  return (
    <div className="px-4 py-4 space-y-4">
      <h1 className="text-lg font-bold">🏦 Налоги</h1>

      {currentTax ? (
        <div className="bg-tg-secondaryBg rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Landmark className="w-5 h-5 text-tg-hint" />
            <span className="text-sm text-tg-hint">{regimeLabels[currentTax.tax_regime] || currentTax.tax_regime}</span>
          </div>
          <div className="text-2xl font-bold mb-1">{formatCurrency(currentTax.remaining_amount)}</div>
          <div className="text-sm text-tg-hint mb-3">к уплате за {currentTax.period}</div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-tg-bg rounded-xl p-3">
              <div className="text-xs text-tg-hint mb-1">Начислено</div>
              <div className="text-sm font-bold">{formatCurrency(currentTax.tax_amount)}</div>
            </div>
            <div className="bg-tg-bg rounded-xl p-3">
              <div className="text-xs text-tg-hint mb-1">Оплачено</div>
              <div className="text-sm font-bold">{formatCurrency(currentTax.paid_amount)}</div>
            </div>
          </div>

          {currentTax.deadline && (
            <div className={`mt-3 p-3 rounded-xl text-sm flex items-center gap-2 ${currentTax.status === 'overdue' ? 'bg-rose-50 text-rose-700 dark:bg-rose-900/20 dark:text-rose-400' : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400'}`}>
              {currentTax.status === 'overdue' ? <AlertTriangle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
              <span>
                {currentTax.status === 'overdue'
                  ? `Просрочен до ${formatDate(currentTax.deadline)}`
                  : `Срок уплаты: ${formatDate(currentTax.deadline)}`}
              </span>
            </div>
          )}
        </div>
      ) : (
        <EmptyState title="Нет данных по налогам" description="Выберите режим налогообложения в настройках" />
      )}

      {taxes && taxes.length > 1 && (
        <div className="bg-tg-secondaryBg rounded-2xl p-4">
          <h2 className="text-sm font-semibold mb-3">История</h2>
          <div className="space-y-2">
            {taxes.map((t) => (
              <div key={t.id} className="flex items-center justify-between text-sm py-2 border-t border-black/5 dark:border-white/10 first:border-t-0">
                <span className="text-tg-hint">{t.period}</span>
                <span className="font-medium">{formatCurrency(t.tax_amount)}</span>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${t.status === 'paid' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400' : t.status === 'overdue' ? 'bg-rose-50 text-rose-700 dark:bg-rose-900/20 dark:text-rose-400' : 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400'}`}>
                  {t.status === 'paid' ? 'Оплачен' : t.status === 'overdue' ? 'Просрочен' : 'Ожидает'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
