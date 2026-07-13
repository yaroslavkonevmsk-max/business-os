import { useParams, useNavigate } from 'react-router-dom'
import { useApi } from '@/hooks/useApi'
import { getDocument } from '@/api/documents'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { formatCurrency, formatDate, formatDateTime } from '@/utils/formatters'
import { ArrowLeft, Download, FileText } from 'lucide-react'
import { useTelegram } from '@/hooks/useTelegram'
import { useEffect } from 'react'

export default function DocumentDetail(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { haptic, showBackButton, hideBackButton } = useTelegram()

  const { data: doc, loading, error } = useApi(() => getDocument(Number(id)), !!id)

  useEffect(() => {
    showBackButton(() => navigate(-1))
    return () => hideBackButton()
  }, [navigate, showBackButton, hideBackButton])

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>
  if (!doc) return <EmptyState title="Документ не найден" />

  const typeLabel = {
    invoice: 'Счёт на оплату',
    act: 'Акт выполненных работ',
    waybill: 'Товарная накладная',
    gph_contract: 'Договор ГПХ',
    report: 'Отчёт',
  }

  const statusLabel = {
    draft: 'Черновик',
    sent: 'Отправлен',
    paid: 'Оплачен',
    cancelled: 'Отменён',
  }

  return (
    <div className="px-4 py-4 space-y-4">
      <button
        onClick={() => { haptic('light'); navigate(-1); }}
        className="flex items-center gap-1 text-sm text-tg-hint hover:text-tg-text transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Назад
      </button>

      <div className="bg-tg-secondaryBg rounded-2xl p-4">
        <div className="flex items-center gap-2 mb-2">
          <FileText className="w-5 h-5 text-tg-hint" />
          <span className="text-xs font-medium text-tg-hint">{typeLabel[doc.type]}</span>
        </div>
        <h1 className="text-lg font-bold mb-1">{doc.number}</h1>
        <div className="text-sm text-tg-hint">{formatDate(doc.date)}</div>

        <div className="flex items-center justify-between mt-4 mb-4 p-3 bg-tg-bg rounded-xl">
          <span className="text-sm">Статус</span>
          <span className="text-sm font-semibold">{statusLabel[doc.status]}</span>
        </div>

        <div className="text-2xl font-bold mb-4">{formatCurrency(doc.total_amount)}</div>

        {doc.items.length > 0 && (
          <div className="space-y-2 mb-4">
            <h3 className="text-sm font-semibold">Позиции</h3>
            {doc.items.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm py-2 border-t border-black/5 dark:border-white/10">
                <div>
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-tg-hint">{item.quantity} {item.unit} × {formatCurrency(item.price)}</div>
                </div>
                <div className="font-semibold">{formatCurrency(item.total)}</div>
              </div>
            ))}
          </div>
        )}

        {doc.due_date && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Срок оплаты:</span> {formatDate(doc.due_date)}
          </div>
        )}
        {doc.prepayment_percent && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Предоплата:</span> {doc.prepayment_percent}%
          </div>
        )}
        {doc.sent_at && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Отправлено:</span> {formatDateTime(doc.sent_at)}
          </div>
        )}
        {doc.notes && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Примечания:</span> {doc.notes}
          </div>
        )}

        {doc.file_url && (
          <a
            href={doc.file_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 flex items-center justify-center gap-2 py-3 bg-tg-button text-tg-buttonText rounded-xl text-sm font-medium active:opacity-80 transition-opacity"
            onClick={() => haptic('medium')}
          >
            <Download className="w-4 h-4" />
            Скачать PDF
          </a>
        )}
      </div>
    </div>
  )
}
