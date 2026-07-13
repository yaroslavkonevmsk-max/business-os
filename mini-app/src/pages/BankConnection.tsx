import { useNavigate } from 'react-router-dom'
import { useApi } from '@/hooks/useApi'
import { useTelegram } from '@/hooks/useTelegram'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { useEffect } from 'react'
import { ArrowLeft, Building2, CheckCircle, XCircle, RefreshCw, ChevronRight } from 'lucide-react'

// Mock API for bank connections
const getBankConnections = async (): Promise<{ items: { id: number; bank_name: string; status: string; account_mask: string | null; last_sync_at: string | null }[] }> => {
  // Fallback: empty array if backend endpoint not available
  return { items: [] }
}

export default function BankConnection(): JSX.Element {
  const navigate = useNavigate()
  const { haptic, showBackButton, hideBackButton } = useTelegram()
  const { data, loading, error } = useApi(getBankConnections)

  useEffect(() => {
    showBackButton(() => navigate(-1))
    return () => hideBackButton()
  }, [navigate, showBackButton, hideBackButton])

  const handleConnect = (bank: string) => {
    haptic('medium')
    // In real app: call backend POST /api/v1/banks/connect { bank_code: bank }
    alert(`Открытие OAuth для ${bank}...`)
  }

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-4 text-center text-rose-500 text-sm">{error}</div>

  return (
    <div className="px-4 py-4 space-y-4">
      <button
        onClick={() => { haptic('light'); navigate(-1); }}
        className="flex items-center gap-1 text-sm text-tg-hint hover:text-tg-text transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Назад
      </button>

      <h1 className="text-lg font-bold">🏦 Подключение банков</h1>

      <div className="space-y-3">
        <button
          onClick={() => handleConnect('tinkoff')}
          className="w-full flex items-center gap-3 bg-tg-secondaryBg rounded-2xl p-4 active:opacity-80 transition-opacity"
        >
          <div className="w-10 h-10 rounded-full bg-yellow-400 flex items-center justify-center text-yellow-900 font-bold text-xs shrink-0">
            Т
          </div>
          <div className="text-left flex-1">
            <div className="text-sm font-semibold">Т-Банк (Тинькофф)</div>
            <div className="text-xs text-tg-hint">Онлайн-авторизация</div>
          </div>
          <ChevronRight />
        </button>

        <button
          onClick={() => handleConnect('sber')}
          className="w-full flex items-center gap-3 bg-tg-secondaryBg rounded-2xl p-4 active:opacity-80 transition-opacity"
        >
          <div className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold text-xs shrink-0">
            С
          </div>
          <div className="text-left flex-1">
            <div className="text-sm font-semibold">СберБанк</div>
            <div className="text-xs text-tg-hint">Онлайн-авторизация</div>
          </div>
          <ChevronRight />
        </button>
      </div>

      {data?.items.length === 0 ? (
        <EmptyState title="Нет подключённых банков" description="Подключите банк для автоматической загрузки платежей" />
      ) : (
        <div className="bg-tg-secondaryBg rounded-2xl p-4 space-y-3">
          <h2 className="text-sm font-semibold">Подключённые</h2>
          {data?.items.map((conn) => (
            <div key={conn.id} className="flex items-center gap-3 py-2 border-t border-black/5 dark:border-white/10 first:border-t-0">
              <Building2 className="w-4 h-4 text-tg-hint" />
              <div className="flex-1">
                <div className="text-sm font-medium">{conn.bank_name}</div>
                <div className="text-xs text-tg-hint">{conn.account_mask || '****'}</div>
              </div>
              <div className="flex items-center gap-1">
                {conn.status === 'active' ? (
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-rose-500" />
                )}
                <span className="text-xs text-tg-hint">{conn.status}</span>
              </div>
              <button
                onClick={() => haptic('light')}
                className="p-1.5 rounded-lg hover:bg-tg-bg transition-colors"
                title="Синхронизировать"
              >
                <RefreshCw className="w-4 h-4 text-tg-hint" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
