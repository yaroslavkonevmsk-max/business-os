import { get, post } from './index'
import { Payment, PaginatedResponse } from '@/types'

export const getPayments = async (page = 1): Promise<PaginatedResponse<Payment>> => {
  const { data } = await get<PaginatedResponse<Payment>>('/api/v1/payments', {
    params: { page, limit: 20 },
  })
  return data
}

export const createPayment = async (payload: Omit<Payment, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<Payment> => {
  const { data } = await post<Payment>('/api/v1/payments', payload)
  return data
}
