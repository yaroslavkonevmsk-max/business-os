import { useState } from 'react'
import { useAuthContext } from '@/context/AuthContext'
import { useApi } from '@/hooks/useApi'
import { useTelegram } from '@/hooks/useTelegram'
import { updateMe, updateSettings, getSettings } from '@/api/users'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { validateInn, validateEmail, validatePhone } from '@/utils/validators'
import { User, UserSettings } from '@/types'
import { Link } from 'react-router-dom'
import { UserCircle, Building2, Bell, CreditCard, ChevronRight, Save } from 'lucide-react'

export default function Settings(): JSX.Element {
  const { user, logout } = useAuthContext()
  const { haptic } = useTelegram()
  const { data: settings, loading: settingsLoading } = useApi(getSettings)

  const [form, setForm] = useState<Partial<User>>({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    email: user?.email || '',
    inn: user?.inn || '',
    ogrn: user?.ogrn || '',
    company_name: user?.company_name || '',
    tax_regime: user?.tax_regime || 'usn_income',
  })

  const [notifications, setNotifications] = useState<Partial<UserSettings>>({
    notifications_enabled: settings?.notifications_enabled ?? true,
    morning_brief_enabled: settings?.morning_brief_enabled ?? true,
    tax_reminders_enabled: settings?.tax_reminders_enabled ?? true,
  })

  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSave = async () => {
    try {
      setSaving(true)
      setMessage('')
      haptic('medium')
      await updateMe(form)
      await updateSettings(notifications)
      setMessage('Сохранено')
      haptic('success')
    } catch {
      setMessage('Ошибка сохранения')
      haptic('error')
    } finally {
      setSaving(false)
    }
  }

  if (settingsLoading) return <LoadingSpinner />

  const isInnValid = !form.inn || validateInn(form.inn)
  const isEmailValid = !form.email || validateEmail(form.email)
  const isPhoneValid = !form.phone || validatePhone(form.phone)
  const isValid = isInnValid && isEmailValid && isPhoneValid

  return (
    <div className="px-4 py-4 space-y-6">
      <h1 className="text-lg font-bold">⚙️ Настройки</h1>

      <div className="bg-tg-secondaryBg rounded-2xl p-4 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <UserCircle className="w-5 h-5 text-tg-hint" />
          <h2 className="text-sm font-semibold">Профиль</h2>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-tg-hint block mb-1">ФИО / Название</label>
            <input
              value={form.full_name || ''}
              onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
              className="w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50"
            />
          </div>
          <div>
            <label className="text-xs text-tg-hint block mb-1">Телефон</label>
            <input
              value={form.phone || ''}
              onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              className={`w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50 ${!isPhoneValid ? 'ring-2 ring-rose-400' : ''}`}
            />
            {!isPhoneValid && <span className="text-xs text-rose-500 mt-1">Неверный формат</span>}
          </div>
          <div>
            <label className="text-xs text-tg-hint block mb-1">Email</label>
            <input
              value={form.email || ''}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className={`w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50 ${!isEmailValid ? 'ring-2 ring-rose-400' : ''}`}
            />
            {!isEmailValid && <span className="text-xs text-rose-500 mt-1">Неверный email</span>}
          </div>
          <div>
            <label className="text-xs text-tg-hint block mb-1">ИНН</label>
            <input
              value={form.inn || ''}
              onChange={(e) => setForm((f) => ({ ...f, inn: e.target.value }))}
              maxLength={12}
              className={`w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50 ${!isInnValid ? 'ring-2 ring-rose-400' : ''}`}
            />
            {!isInnValid && <span className="text-xs text-rose-500 mt-1">Неверный ИНН</span>}
          </div>
          <div>
            <label className="text-xs text-tg-hint block mb-1">ОГРН</label>
            <input
              value={form.ogrn || ''}
              onChange={(e) => setForm((f) => ({ ...f, ogrn: e.target.value }))}
              maxLength={15}
              className="w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50"
            />
          </div>
          <div>
            <label className="text-xs text-tg-hint block mb-1">Название компании</label>
            <input
              value={form.company_name || ''}
              onChange={(e) => setForm((f) => ({ ...f, company_name: e.target.value }))}
              className="w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50"
            />
          </div>
        </div>
      </div>

      <div className="bg-tg-secondaryBg rounded-2xl p-4 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Building2 className="w-5 h-5 text-tg-hint" />
          <h2 className="text-sm font-semibold">Налогообложение</h2>
        </div>
        <select
          value={form.tax_regime || ''}
          onChange={(e) => setForm((f) => ({ ...f, tax_regime: e.target.value as User['tax_regime'] }))}
          className="w-full px-3 py-2 bg-tg-bg rounded-xl text-sm outline-none focus:ring-2 focus:ring-tg-button/50"
        >
          <option value="usn_income">УСН Доходы (6%)</option>
          <option value="usn_income_expense">УСН Доходы минус Расходы (15%)</option>
          <option value="npd">Налог на проф. доход (НПД)</option>
          <option value="patent">Патент</option>
        </select>
      </div>

      <div className="bg-tg-secondaryBg rounded-2xl p-4 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Bell className="w-5 h-5 text-tg-hint" />
          <h2 className="text-sm font-semibold">Уведомления</h2>
        </div>
        <div className="space-y-3">
          <label className="flex items-center justify-between text-sm">
            <span>Включены</span>
            <input
              type="checkbox"
              checked={notifications.notifications_enabled}
              onChange={(e) => setNotifications((n) => ({ ...n, notifications_enabled: e.target.checked }))}
              className="w-5 h-5 accent-tg-button"
            />
          </label>
          <label className="flex items-center justify-between text-sm">
            <span>Утренний брифинг</span>
            <input
              type="checkbox"
              checked={notifications.morning_brief_enabled}
              onChange={(e) => setNotifications((n) => ({ ...n, morning_brief_enabled: e.target.checked }))}
              className="w-5 h-5 accent-tg-button"
            />
          </label>
          <label className="flex items-center justify-between text-sm">
            <span>Налоговые напоминания</span>
            <input
              type="checkbox"
              checked={notifications.tax_reminders_enabled}
              onChange={(e) => setNotifications((n) => ({ ...n, tax_reminders_enabled: e.target.checked }))}
              className="w-5 h-5 accent-tg-button"
            />
          </label>
        </div>
      </div>

      <Link
        to="/bank-connection"
        className="flex items-center justify-between bg-tg-secondaryBg rounded-2xl p-4 text-sm"
      >
        <div className="flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-tg-hint" />
          <span className="font-medium">Банки</span>
        </div>
        <ChevronRight className="w-4 h-4 text-tg-hint" />
      </Link>

      <button
        onClick={handleSave}
        disabled={saving || !isValid}
        className="w-full flex items-center justify-center gap-2 py-3 bg-tg-button text-tg-buttonText rounded-xl text-sm font-medium disabled:opacity-50 active:opacity-80 transition-opacity"
      >
        <Save className="w-4 h-4" />
        {saving ? 'Сохранение...' : 'Сохранить'}
      </button>

      {message && (
        <div className="text-center text-sm text-tg-hint">{message}</div>
      )}

      <button
        onClick={logout}
        className="w-full py-3 text-rose-500 text-sm font-medium rounded-xl bg-rose-50 dark:bg-rose-900/20 active:opacity-80 transition-opacity"
      >
        Выйти
      </button>
    </div>
  )
}
