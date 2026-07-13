import { get, patch } from './index'
import { User, UserSettings } from '@/types'

export const getMe = async (): Promise<User> => {
  const { data } = await get<User>('/api/v1/users/me')
  return data
}

export const updateMe = async (payload: Partial<User>): Promise<User> => {
  const { data } = await patch<User>('/api/v1/users/me', payload)
  return data
}

export const getSettings = async (): Promise<UserSettings> => {
  const { data } = await get<UserSettings>('/api/v1/users/me/settings')
  return data
}

export const updateSettings = async (payload: Partial<UserSettings>): Promise<UserSettings> => {
  const { data } = await patch<UserSettings>('/api/v1/users/me/settings', payload)
  return data
}
