import { post } from './index'
import { AuthResponse } from '@/types'

export const loginWithTelegram = async (initData: string): Promise<AuthResponse> => {
  const { data } = await post<AuthResponse>('/api/v1/auth/telegram', { init_data: initData })
  return data
}
