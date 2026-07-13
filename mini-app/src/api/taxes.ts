import { get } from './index'
import { TaxCalculation } from '@/types'

export const getTaxes = async (): Promise<TaxCalculation[]> => {
  const { data } = await get<TaxCalculation[]>('/api/v1/taxes')
  return data
}

export const getCurrentTax = async (): Promise<TaxCalculation> => {
  const { data } = await get<TaxCalculation>('/api/v1/taxes/current')
  return data
}
