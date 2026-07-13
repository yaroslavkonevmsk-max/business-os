import { useState, useEffect, useCallback } from 'react'
import { AxiosError } from 'axios'

type ApiFunction<T> = () => Promise<T>

interface UseApiResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useApi<T>(fetchFn: ApiFunction<T>, immediate = true): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState<string | null>(null)

  const execute = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await fetchFn()
      setData(result)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string; message?: string }>
      const message =
        axiosError.response?.data?.detail ||
        axiosError.response?.data?.message ||
        axiosError.message ||
        'Ошибка загрузки данных'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  const refetch = useCallback(() => {
    execute()
  }, [execute])

  useEffect(() => {
    if (immediate) {
      execute()
    }
  }, [execute, immediate])

  return { data, loading, error, refetch }
}
