import { apiClient } from './client'

export interface LoginRequest {
  username: string // FastAPI OAuth2 uses username field for email
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    
    const response = await apiClient.post<AuthResponse>('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async register(data: RegisterRequest) {
    const response = await apiClient.post('/api/auth/register', data)
    return response.data
  }
}