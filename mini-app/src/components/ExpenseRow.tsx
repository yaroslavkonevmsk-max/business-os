import { Expense } from '@/types'
import { formatCurrency, formatDate } from '@/utils/formatters'

interface ExpenseRowProps {
  expense: Expense
}

const categoryLabels: Record<string, string> = {
  rent: 'Аренда',
  software: 'Программы',
  hardware: 'Оборудование',
  transport: 'Транспорт',
  marketing: 'Маркетинг',
  office: 'Офис',
  taxes: 'Налоги',
  salary: 'Зарплата',
  other: 'Прочее',
}

export function ExpenseRow({ expense }: ExpenseRowProps): JSX.Element {
  return (
    <div className="flex items-center gap-3 py-3 px-4 bg-tg-secondaryBg rounded-xl">
      <div className="w-9 h-9 rounded-full bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400 flex items-center justify-center shrink-0 font-bold text-xs">
        {categoryLabels[expense.category] || expense.category}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">{expense.description || categoryLabels[expense.category] || expense.category}</div>
        <div className="text-xs text-tg-hint">{formatDate(expense.date)}</div>
      </div>
      <div className="text-sm font-bold text-rose-600 dark:text-rose-400 shrink-0">
        -{formatCurrency(expense.amount)}
      </div>
    </div>
  )
}
