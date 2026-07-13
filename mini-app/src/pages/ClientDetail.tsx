import { useParams, useNavigate } from 'react-router-dom'
import { useApi } from '@/hooks/useApi'
import { getClient } from '@/api/clients'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { ArrowLeft, Phone, Mail, Building2, Briefcase, User } from 'lucide-react'
import { useTelegram } from '@/hooks/useTelegram'
import { useEffect } from 'react'

export default function ClientDetail(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { haptic, showBackButton, hideBackButton } = useTelegram()

  const { data: client, loading, error } = useApi(() => getClient(Number(id)), !!id)

  useEffect(() => {
    showBackButton(() => navigate(-1))
    return () => hideBackButton()
  }, [navigate, showBackButton, hideBackButton])

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>
  if (!client) return <EmptyState title="Клиент не найден" />

  const typeIcon = {
    individual: <User className="w-5 h-5" />,
    company: <Building2 className="w-5 h-5" />,
    ip: <Briefcase className="w-5 h-5" />,
  }

  const typeLabel = {
    individual: 'Физическое лицо',
    company: 'Компания',
    ip: 'Индивидуальный предприниматель',
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
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-full bg-tg-button/10 text-tg-button flex items-center justify-center shrink-0">
            {typeIcon[client.type]}
          </div>
          <div>
            <h1 className="text-lg font-bold">{client.name}</h1>
            <p className="text-xs text-tg-hint">{typeLabel[client.type]}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-tg-bg rounded-xl p-3">
            <div className="text-xs text-tg-hint mb-1">Выручка</div>
            <div className="text-sm font-bold">{formatCurrency(client.total_revenue)}</div>
          </div>
          <div className="bg-tg-bg rounded-xl p-3">
            <div className="text-xs text-tg-hint mb-1">Сделок</div>
            <div className="text-sm font-bold">{client.deals_count}</div>
          </div>
        </div>

        {client.inn && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">ИНН:</span> {client.inn}
          </div>
        )}
        {client.phone && (
          <div className="flex items-center gap-2 text-sm py-2 border-t border-black/5 dark:border-white/10">
            <Phone className="w-4 h-4 text-tg-hint" />
            <a href={`tel:${client.phone}`} className="text-tg-link">{client.phone}</a>
          </div>
        )}
        {client.email && (
          <div className="flex items-center gap-2 text-sm py-2 border-t border-black/5 dark:border-white/10">
            <Mail className="w-4 h-4 text-tg-hint" />
            <a href={`mailto:${client.email}`} className="text-tg-link">{client.email}</a>
          </div>
        )}
        {client.first_payment_date && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Первый платёж:</span> {formatDate(client.first_payment_date)}
          </div>
        )}
        {client.last_payment_date && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Последний платёж:</span> {formatDate(client.last_payment_date)}
          </div>
        )}
        {client.notes && (
          <div className="text-sm py-2 border-t border-black/5 dark:border-white/10">
            <span className="text-tg-hint">Примечания:</span> {client.notes}
          </div>
        )}
      </div>
    </div>
  )
}
