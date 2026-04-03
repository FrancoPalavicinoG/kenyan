import { CheckinCreate, CheckinResponse } from '../types/checkin'
import apiClient from './client'

export const checkinApi = {
  getToday: (): Promise<CheckinResponse | null> =>
    apiClient.get('/checkins/today').then(r => r.data),

  create: (payload: CheckinCreate): Promise<CheckinResponse> =>
    apiClient.post('/checkins', payload).then(r => r.data),
}
