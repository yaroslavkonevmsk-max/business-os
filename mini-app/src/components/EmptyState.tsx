import { Inbox } from 'lucide-react'

interface EmptyStateProps {
  title?: string
  description?: string
  icon?: React.ReactNode
}

export function EmptyState({
  title = 'Нет данных',
  description = 'Пока здесь ничего нет',
  icon,
}: EmptyStateProps): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="text-tg-hint mb-3">
        {icon || <Inbox className="w-10 h-10" />}
      </div>
      <h3 className="text-base font-semibold mb-1">{title}</h3>
      <p className="text-sm text-tg-hint">{description}</p>
    </div>
  )
}
