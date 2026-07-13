import { get, post } from './index'
import { Document, PaginatedResponse } from '@/types'

export const getDocuments = async (page = 1, type?: string): Promise<PaginatedResponse<Document>> => {
  const { data } = await get<PaginatedResponse<Document>>('/api/v1/documents', {
    params: { page, type, limit: 20 },
  })
  return data
}

export const getDocument = async (id: number): Promise<Document> => {
  const { data } = await get<Document>(`/api/v1/documents/${id}`)
  return data
}

export const createDocument = async (payload: Omit<Document, 'id' | 'user_id' | 'file_url' | 'file_size' | 'file_hash' | 'sent_at' | 'sent_method' | 'created_at' | 'updated_at'>): Promise<Document> => {
  const { data } = await post<Document>('/api/v1/documents', payload)
  return data
}
