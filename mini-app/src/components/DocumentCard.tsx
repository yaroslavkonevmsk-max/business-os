import { Document } from '@/types'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { FileText, CheckCircle, Clock, XCircle, Send } from 'lucide-react'

interface DocumentCardProps {
  document: Document
}

export function DocumentCard({ document }: DocumentCardProps): JSX.Element {
  const statusConfig = {
    draft: { icon: Clock, label: 'Черновик', color: 'text-amber-500' },
    sent: { icon: Send, label: 'Отправлен', color: 'text-sky-500' },
    paid: { icon: CheckCircle, label: 'Оплачен', color: 'text-emerald-500' },
    cancelled: { icon: XCircle, label: 'Отменён', color: 'text-rose-500' },
  }

  const typeLabel = {
    invoice: 'Счёт',
    act: 'Акт',
    waybill: 'Накладная',
    gph_contract: 'Договор ГПХ',
    report: 'Отчёт',
  }

  const StatusIcon = statusConfig[document.status].icon

  return (
    <div className="bg-tg-secondaryBg rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-tg-hint" />
          <span className="text-xs font-medium text-tg-hint">{typeLabel[document.type]}</span>
        </div>
        <div className={`flex items-center gap-1 text-xs font-medium ${statusConfig[document.status].color}`}>
          <StatusIcon className="w-3.5 h-3.5" />
          {statusConfig[document.status].label}
        </div>
      </div>
      <div className="font-semibold text-sm">{document.number}</div>
      <div className="text-xs text-tg-hint mt-0.5">{formatDate(document.date)}</div>
      <div className="flex items-center justify-between mt-3">
        <div className="text-sm font-bold">{formatCurrency(document.total_amount)}</div>
        {document.file_url && (
          <a
            href={document.file_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-tg-link font-medium"
            onClick={(e) => e.stopPropagation()}
          >
            PDF
          </a>
        )}
      </div>
    </div>
  )
}
