export interface User {
  id: number
  telegram_id: string
  username: string | null
  full_name: string
  phone: string | null
  email: string | null
  inn: string | null
  ogrn: string | null
  company_name: string | null
  tax_regime: 'usn_income' | 'usn_income_expense' | 'npd' | 'patent' | null
  bank_details: BankDetails | null
  tariff: 'free' | 'basic' | 'pro' | 'business'
  tariff_expires_at: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BankDetails {
  bank_name: string
  account_number: string
  bik: string
  corr_account: string
}

export interface UserSettings {
  id: number
  user_id: number
  notifications_enabled: boolean
  morning_brief_enabled: boolean
  morning_brief_time: string
  tax_reminders_enabled: boolean
  language: string
  currency: string
  timezone: string
}

export interface Client {
  id: number
  user_id: number
  name: string
  type: 'individual' | 'company' | 'ip'
  inn: string | null
  phone: string | null
  email: string | null
  total_revenue: string
  deals_count: number
  first_payment_date: string | null
  last_payment_date: string | null
  notes: string | null
  auto_created: boolean
  source: string
  created_at: string
  updated_at: string
}

export interface Payment {
  id: number
  user_id: number
  client_id: number | null
  bank_connection_id: number | null
  amount: string
  currency: string
  date: string
  description: string | null
  parsed_client_name: string | null
  bank_transaction_id: string | null
  bank_name: string | null
  payment_type: 'income' | 'expense'
  category: string | null
  document_id: number | null
  is_tax_calculated: boolean
  created_at: string
  updated_at: string
}

export interface Expense {
  id: number
  user_id: number
  amount: string
  date: string
  category: string
  description: string | null
  receipt_url: string | null
  ai_category: string | null
  is_manual_category: boolean
  created_at: string
  updated_at: string
}

export interface DocumentItem {
  name: string
  quantity: string
  unit: string
  price: string
  total: string
}

export interface Document {
  id: number
  user_id: number
  client_id: number
  type: 'invoice' | 'act' | 'waybill' | 'gph_contract' | 'report'
  number: string
  total_amount: string
  date: string
  status: 'draft' | 'sent' | 'paid' | 'cancelled'
  file_url: string | null
  file_size: number | null
  file_hash: string | null
  payment_id: number | null
  items: DocumentItem[]
  due_date: string | null
  notes: string | null
  prepayment_percent: number | null
  sent_at: string | null
  sent_method: string | null
  created_at: string
  updated_at: string
}

export interface TaxCalculation {
  id: number
  user_id: number
  tax_regime: string
  period: string
  total_income: string
  total_expenses: string
  tax_base: string
  tax_rate: string
  tax_amount: string
  paid_amount: string
  remaining_amount: string
  deadline: string | null
  status: 'pending' | 'paid' | 'overdue'
  created_at: string
  updated_at: string
}

export interface BankConnection {
  id: number
  user_id: number
  bank_code: string
  bank_name: string
  account_number: string | null
  account_mask: string | null
  status: 'active' | 'expired' | 'error'
  token_expires_at: string | null
  last_sync_at: string | null
  last_sync_error: string | null
  created_at: string
  updated_at: string
}

export interface Subscription {
  id: number
  user_id: number
  tariff: string
  status: 'active' | 'cancelled' | 'expired'
  payment_provider: string
  payment_id: string | null
  amount: string
  currency: string
  period_start: string
  period_end: string
  auto_renew: boolean
  created_at: string
  updated_at: string
}

export interface PulseData {
  period: string
  total_revenue: string
  revenue_change_percent: number
  total_expenses: string
  profit: string
  tax_amount: string
  tax_deadline: string | null
  tax_days_remaining: number
  new_clients_count: number
  repeat_clients_count: number
  total_clients_count: number
  top_client: {
    id: number
    name: string
    total_revenue: string
  } | null
  documents_created: number
  average_check: string
  ai_insight: string | null
}

export interface AnalyticsPeriod {
  period: string
  revenue: string
  expenses: string
  profit: string
  new_clients: number
  repeat_clients: number
}

export interface RevenueAnalytics {
  periods: AnalyticsPeriod[]
}

export interface ExpenseCategory {
  category: string
  amount: string
  percentage: number
}

export interface ExpenseAnalytics {
  categories: ExpenseCategory[]
  total: string
}

export interface ClientAnalytics {
  periods: {
    period: string
    new_clients: number
    repeat_clients: number
    total_clients: number
  }[]
}

export interface AuthResponse {
  access_token: string
  user: User
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pages: number
}
