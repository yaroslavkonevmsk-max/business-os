import { useState, useCallback } from 'react'
import { useApi } from '@/hooks/useApi'
import { getDocuments } from '@/api/documents'
import { DocumentCard } from '@/components/DocumentCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { FileText } from 'lucide-react'

type DocFilter = 'all' | 'invoice' | 'act' | 'waybill' | 'gph_contract' | 'report'

const filters: { key: DocFilter; label: string }[] = [
  { key: 'all', label: 'Все' },
  { key: 'invoice', label: 'Счета' },
  { key: 'act', label: 'Акты' },
  { key: 'waybill', label: 'Накладные' },
  { key: 'gph_contract', label: 'ГПХ' },
  { key: 'report', label: 'Отчёты' },
]

export default function Documents(): JSX.Element {
  const [filter, setFilter] = useState<DocFilter>('all')
  const [page, setPage] = useState(1)

  const fetchDocuments = useCallback(
    () => getDocuments(page, filter === 'all' ? undefined : filter),
    [page, filter]
  )
  const { data, loading, error, refetch } = useApi(fetchDocuments)

  return (
    <div className="px-4 py-4 space-y-4">
      <h1 className="text-lg font-bold">📄 Документы</h1>

      <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => { setFilter(f.key); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              filter === f.key
                ? 'bg-tg-button text-tg-buttonText'
                : 'bg-tg-secondaryBg text-tg-text'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading && <LoadingSpinner />}
      {error && <div className="text-center text-rose-500 text-sm py-4">{error}</div>}
      {!loading && !error && data?.items.length === 0 && (
        <EmptyState title="Нет документов" description="Создайте первый документ через бота" icon={<FileText className="w-10 h-10" />} />
      )}

      <div className="space-y-3">
        {data?.items.map((doc) => (
          <DocumentCard key={doc.id} document={doc} />
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
