import { Payment } from '@/types'
import { formatCurrency, formatDateTime } from '@/utils/formatters'
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react'

interface PaymentRowProps {
  payment: Payment
}

export function PaymentRow({ payment }: PaymentRowProps): JSX.Element {
  const isIncome = payment.payment_type === 'income'

  return (
    <div className="flex items-center gap-3 py-3 px-4 bg-tg-secondaryBg rounded-xl">
      <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${isIncome ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-rose-50 text-rose-600 dark:bg-rose-900/20 dark:text-rose-400'}`}>
        {isIncome ? <ArrowDownLeft className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">
          {payment.description || (isIncome ? 'Поступление' : 'Списание')}
        </div>
        <div className="text-xs text-tg-hint">
          {payment.parsed_client_name || payment.category || '—'} • {formatDateTime(payment.date)}
        </div>
      </div>
      <div className={`text-sm font-bold shrink-0 ${isIncome ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
        {isIncome ? '+' : '-'}{formatCurrency(payment.amount)}
      </div>
    </div>
  )
}
