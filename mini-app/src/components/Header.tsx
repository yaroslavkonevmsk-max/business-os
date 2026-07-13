import { useAuthContext } from '@/context/AuthContext'
import { useTheme } from '@/hooks/useTheme'
import { Settings } from 'lucide-react'
import { Link } from 'react-router-dom'

export function Header(): JSX.Element {
  const { user } = useAuthContext()
  const { dark } = useTheme()

  return (
    <header className="sticky top-0 z-50 bg-tg-bg/80 backdrop-blur-md border-b border-black/5 dark:border-white/10 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${dark ? 'bg-tg-button text-tg-buttonText' : 'bg-tg-button text-tg-buttonText'}`}>
          {user?.full_name?.charAt(0).toUpperCase() || '?'}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold leading-tight">{user?.full_name || 'Гость'}</span>
          <span className="text-xs text-tg-hint">{user?.company_name || 'ИП'}</span>
        </div>
      </div>
      <Link
        to="/settings"
        className="p-2 rounded-lg hover:bg-tg-secondaryBg transition-colors"
        aria-label="Настройки"
      >
        <Settings className="w-5 h-5 text-tg-text" />
      </Link>
    </header>
  )
}
