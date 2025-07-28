import { apiClient } from './client'

export const photosApi = {
  async uploadMonthlyPhoto(year: number, month: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post(`/api/photos/upload/${year}/${month}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async getMonthlyPhoto(year: number, month: number) {
    const response = await apiClient.get(`/api/photos/${year}/${month}`)
    return response.data
  }
}