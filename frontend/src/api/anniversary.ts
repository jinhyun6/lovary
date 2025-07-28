import { apiClient } from './client'

export interface Anniversary {
  id: number
  date: string
  name: string
  user_id: number
  partner_id: number
}

export interface AnniversaryCreate {
  date: string
  name: string
}

export const anniversaryApi = {
  async createOrUpdate(data: AnniversaryCreate): Promise<Anniversary> {
    const response = await apiClient.post<Anniversary>('/api/anniversary/', data)
    return response.data
  },

  async getAll(): Promise<Anniversary[]> {
    const response = await apiClient.get<Anniversary[]>('/api/anniversary/')
    return response.data
  },

  async getMonthAnniversaries(year: number, month: number): Promise<Record<number, { name: string, date: string }>> {
    const response = await apiClient.get(`/api/anniversary/month/${year}/${month}`)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/anniversary/${id}`)
  }
}