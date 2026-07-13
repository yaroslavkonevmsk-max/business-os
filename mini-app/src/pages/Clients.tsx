import { useState, useCallback } from 'react'
import { useApi } from '@/hooks/useApi'
import { useTelegram } from '@/hooks/useTelegram'
import { getClients } from '@/api/clients'
import { ClientCard } from '@/components/ClientCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { Search, UserPlus } from 'lucide-react'

export default function Clients(): JSX.Element {
  const { haptic } = useTelegram()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const fetchClients = useCallback(() => getClients(page, search), [page, search])
  const { data, loading, error, refetch } = useApi(fetchClients)

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(1)
  }

  return (
    <div className="px-4 py-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">👥 Клиенты</h1>
        <button
          onClick={() => { haptic('medium'); /* open add modal */ }}
          className="p-2 bg-tg-button text-tg-buttonText rounded-xl"
        >
          <UserPlus className="w-4 h-4" />
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-tg-hint" />
        <input
          type="text"
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Поиск по имени или ИНН"
          className="w-full pl-9 pr-4 py-3 bg-tg-secondaryBg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50 placeholder:text-tg-hint"
        />
      </div>

      {loading && <LoadingSpinner />}
      {error && <div className="text-center text-rose-500 text-sm py-4">{error}</div>}
      {!loading && !error && data?.items.length === 0 && (
        <EmptyState title="Нет клиентов" description="Добавьте первого клиента" />
      )}

      <div className="space-y-3">
        {data?.items.map((client) => (
          <ClientCard key={client.id} client={client} />
        ))}
      </div>

      {data && data.pages > 1 && (
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
