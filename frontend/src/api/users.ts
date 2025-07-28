import { apiClient } from './client'

export interface User {
  id: number
  email: string
  name?: string
  partner_id?: number
  reminder_time?: string
  created_at: string
}

export interface UserUpdate {
  name?: string
  reminder_time?: string
}

export interface PartnerRequest {
  id: number
  requester_id: number
  recipient_id: number
  status: string
  created_at: string
  requester: User
  recipient: User
}

export interface PushSubscription {
  endpoint: string
  keys: {
    p256dh: string
    auth: string
  }
}

export const usersApi = {
  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/api/users/me')
    return response.data
  },

  async updateMe(data: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>('/api/users/me', data)
    return response.data
  },

  async searchUsers(email: string): Promise<Array<{id: number, email: string, name?: string}>> {
    const response = await apiClient.get('/api/users/search', { params: { email } })
    return response.data
  },

  async sendPartnerRequest(recipientEmail: string): Promise<PartnerRequest> {
    const response = await apiClient.post<PartnerRequest>('/api/users/partner-request', {
      recipient_email: recipientEmail
    })
    return response.data
  },

  async getPartnerRequests(): Promise<PartnerRequest[]> {
    const response = await apiClient.get<PartnerRequest[]>('/api/users/partner-requests')
    return response.data
  },

  async acceptPartnerRequest(requestId: number) {
    const response = await apiClient.put(`/api/users/partner-request/${requestId}/accept`)
    return response.data
  },

  async rejectPartnerRequest(requestId: number) {
    const response = await apiClient.put(`/api/users/partner-request/${requestId}/reject`)
    return response.data
  },

  async savePushSubscription(subscription: PushSubscriptionJSON) {
    const response = await apiClient.post('/api/users/push-subscription', {
      endpoint: subscription.endpoint,
      keys: subscription.keys
    })
    return response.data
  },

  async disconnectPartner() {
    const response = await apiClient.delete('/api/users/partner/disconnect')
    return response.data
  },

  async deleteAccount() {
    const response = await apiClient.delete('/api/users/account')
    return response.data
  }
}