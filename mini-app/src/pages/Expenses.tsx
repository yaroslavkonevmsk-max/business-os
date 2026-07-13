import { useState, useCallback } from 'react'
import { useApi } from '@/hooks/useApi'
import { useTelegram } from '@/hooks/useTelegram'
import { ExpenseRow } from '@/components/ExpenseRow'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { post } from '@/api'
import { Expense } from '@/types'
import { Receipt, Plus } from 'lucide-react'

// Mock API for expenses since the spec doesn't list a dedicated module
const getExpenses = async (page = 1): Promise<{ items: Expense[]; total: number; page: number; pages: number }> => {
  const { data } = await post('/api/v1/expenses/list', { page, limit: 20 })
  return data as { items: Expense[]; total: number; page: number; pages: number }
}

export default function Expenses(): JSX.Element {
  const { haptic } = useTelegram()
  const [page, setPage] = useState(1)

  const fetchExpenses = useCallback(() => getExpenses(page), [page])
  const { data, loading, error, refetch } = useApi(fetchExpenses)

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>
  if (!data || data.items.length === 0) return <EmptyState title="Нет расходов" description="Добавьте первый расход" icon={<Receipt className="w-10 h-10" />} />

  return (
    <div className="px-4 py-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">📉 Расходы</h1>
        <button
          onClick={() => { haptic('medium'); /* open add modal */ }}
          className="p-2 bg-tg-button text-tg-buttonText rounded-xl"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
      <div className="space-y-2">
        {data.items.map((expense) => (
          <ExpenseRow key={expense.id} expense={expense} />
        ))}
      </div>
      {data.pages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <button
            disabled={page <= 1}
            onClick={() => { setPage(p => p - 1); refetch(); }}
            className="px-3 py-2 text-sm bg-tg-secondaryBg rounded-lg disabled:opacity-40"
          >
            Назад
          </button>
          <span className="text-xs text-tg-hint">{page} / {data.pages}</span>
          <button
            disabled={page >= data.pages}
            onClick={() => { setPage(p => p + 1); refetch(); }}
            className="px-3 py-2 text-sm bg-tg-secondaryBg rounded-lg disabled:opacity-40"
          >
            Вперёд
          </button>
        </div>
      )}
    </div>
  )
}
