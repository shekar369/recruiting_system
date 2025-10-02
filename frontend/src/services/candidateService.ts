import api from './api'

export interface Candidate {
  id?: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  location?: string
  linkedin_url?: string
  github_url?: string
  portfolio_url?: string
  years_of_experience?: number
  current_job_title?: string
  current_company?: string
  expected_salary_min?: number
  expected_salary_max?: number
  currency?: string
  availability?: string
  status?: string
  source?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface CandidateListResponse {
  total: number
  page: number
  size: number
  candidates: Candidate[]
}

export const candidateService = {
  getAll: async (page: number = 1, size: number = 10) => {
    const response = await api.get<CandidateListResponse>('/api/v1/candidates', {
      params: { page, size }
    })
    return response.data
  },

  getById: async (id: string) => {
    const response = await api.get(`/api/v1/candidates/${id}`)
    return response.data
  },

  create: async (candidate: Candidate) => {
    const response = await api.post('/api/v1/candidates', candidate)
    return response.data
  },

  update: async (id: string, candidate: Partial<Candidate>) => {
    const response = await api.put(`/api/v1/candidates/${id}`, candidate)
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(`/api/v1/candidates/${id}`)
    return response.data
  },

  uploadResume: async (candidateId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(
      `/api/v1/candidates/${candidateId}/resumes`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    return response.data
  },

  search: async (query: string, filters: any = {}) => {
    const response = await api.post('/api/v1/search/candidates', {
      query,
      filters
    })
    return response.data
  }
}
