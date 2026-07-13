import { useNavigate } from 'react-router-dom'
import { Client } from '@/types'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { User, Building2, Briefcase } from 'lucide-react'

interface ClientCardProps {
  client: Client
}

export function ClientCard({ client }: ClientCardProps): JSX.Element {
  const navigate = useNavigate()

  const typeIcon = {
    individual: <User className="w-4 h-4" />,
    company: <Building2 className="w-4 h-4" />,
    ip: <Briefcase className="w-4 h-4" />,
  }

  const typeLabel = {
    individual: 'Физлицо',
    company: 'Компания',
    ip: 'ИП',
  }

  return (
    <button
      onClick={() => navigate(`/clients/${client.id}`)}
      className="w-full text-left bg-tg-secondaryBg rounded-xl p-4 hover:opacity-80 transition-opacity active:scale-[0.98] transform"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-tg-button/10 text-tg-button flex items-center justify-center shrink-0">
          {typeIcon[client.type]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm truncate">{client.name}</div>
          <div className="text-xs text-tg-hint mt-0.5">
            {typeLabel[client.type]} • {client.deals_count} сделок
          </div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-sm font-bold">{formatCurrency(client.total_revenue)}</div>
          <div className="text-xs text-tg-hint">{client.last_payment_date ? `Посл. ${formatDate(client.last_payment_date)}` : 'Нет платежей'}</div>
        </div>
      </div>
      {client.inn && (
        <div className="text-xs text-tg-hint mt-2">ИНН: {client.inn}</div>
      )}
    </button>
  )
}
