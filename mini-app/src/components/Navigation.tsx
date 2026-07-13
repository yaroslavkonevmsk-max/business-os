import { useLocation, useNavigate } from 'react-router-dom'
import { useTelegram } from '@/hooks/useTelegram'
import { LayoutDashboard, Users, FileText, BarChart3, Settings } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Пульс', icon: LayoutDashboard },
  { path: '/clients', label: 'Клиенты', icon: Users },
  { path: '/documents', label: 'Документы', icon: FileText },
  { path: '/analytics', label: 'Аналитика', icon: BarChart3 },
  { path: '/settings', label: 'Настройки', icon: Settings },
]

export function Navigation(): JSX.Element {
  const location = useLocation()
  const navigate = useNavigate()
  const { haptic } = useTelegram()

  const handleClick = (path: string) => {
    haptic('light')
    navigate(path)
  }

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-tg-bg/90 backdrop-blur-md border-t border-black/5 dark:border-white/10 safe-area-pb">
      <div className="flex items-center justify-around h-16">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || location.pathname.startsWith(`${item.path}/`)
          const Icon = item.icon
          return (
            <button
              key={item.path}
              onClick={() => handleClick(item.path)}
              className={`flex flex-col items-center gap-1 px-3 py-1 rounded-lg transition-colors ${
                isActive ? 'text-tg-button' : 'text-tg-hint'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
