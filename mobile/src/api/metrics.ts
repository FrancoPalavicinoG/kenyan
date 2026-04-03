import { TodayMetrics } from '../types/metrics'
import apiClient from './client'

export const metricsApi = {
  getToday: (): Promise<TodayMetrics> =>
    apiClient.get('/metrics/today').then(r => r.data),
}
