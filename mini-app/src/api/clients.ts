import { get, post, put, del } from './index'
import { Client, PaginatedResponse } from '@/types'

export const getClients = async (page = 1, search = ''): Promise<PaginatedResponse<Client>> => {
  const { data } = await get<PaginatedResponse<Client>>('/api/v1/clients', {
    params: { page, search, limit: 20 },
  })
  return data
}

export const getClient = async (id: number): Promise<Client> => {
  const { data } = await get<Client>(`/api/v1/clients/${id}`)
  return data
}

export const createClient = async (payload: Omit<Client, 'id' | 'user_id' | 'total_revenue' | 'deals_count' | 'first_payment_date' | 'last_payment_date' | 'auto_created' | 'source' | 'created_at' | 'updated_at'>): Promise<Client> => {
  const { data } = await post<Client>('/api/v1/clients', payload)
  return data
}

export const updateClient = async (id: number, payload: Partial<Client>): Promise<Client> => {
  const { data } = await put<Client>(`/api/v1/clients/${id}`, payload)
  return data
}

export const deleteClient = async (id: number): Promise<void> => {
  await del(`/api/v1/clients/${id}`)
}
