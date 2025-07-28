import { apiClient } from './client'

export interface DiaryCreate {
  title: string
  content: string
}

export interface Diary {
  id: number
  title: string
  content: string
  author_id: number
  created_at: string
  is_read_by_partner: boolean
}

export const diaryApi = {
  async createDiary(data: DiaryCreate): Promise<Diary> {
    const response = await apiClient.post<Diary>('/api/diary/', data)
    return response.data
  },

  async updateDiary(diaryId: number, data: DiaryCreate): Promise<Diary> {
    const response = await apiClient.put<Diary>(`/api/diary/${diaryId}`, data)
    return response.data
  },

  async getMyDiaries(): Promise<Diary[]> {
    const response = await apiClient.get<Diary[]>('/api/diary/my')
    return response.data
  },

  async getPartnerDiaries(): Promise<Diary[]> {
    const response = await apiClient.get<Diary[]>('/api/diary/partner')
    return response.data
  },

  async getMonthDiaries(year: number, month: number) {
    const response = await apiClient.get(`/api/diary/month/${year}/${month}`)
    return response.data
  },

  async getDayDiaries(year: number, month: number, day: number) {
    const response = await apiClient.get(`/api/diary/date/${year}/${month}/${day}`)
    return response.data
  }
}