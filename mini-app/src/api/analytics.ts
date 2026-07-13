import { get } from './index'
import { PulseData, RevenueAnalytics, ExpenseAnalytics, ClientAnalytics } from '@/types'

export const getPulse = async (): Promise<PulseData> => {
  const { data } = await get<PulseData>('/api/v1/analytics/pulse')
  return data
}

export const getRevenueAnalytics = async (period: 'month' | 'quarter' | 'year'): Promise<RevenueAnalytics> => {
  const { data } = await get<RevenueAnalytics>('/api/v1/analytics/revenue', {
    params: { period },
  })
  return data
}

export const getExpenseAnalytics = async (period: 'month' | 'quarter' | 'year'): Promise<ExpenseAnalytics> => {
  const { data } = await get<ExpenseAnalytics>('/api/v1/analytics/expenses', {
    params: { period },
  })
  return data
}

export const getClientAnalytics = async (period: 'month' | 'quarter' | 'year'): Promise<ClientAnalytics> => {
  const { data } = await get<ClientAnalytics>('/api/v1/analytics/clients', {
    params: { period },
  })
  return data
}
