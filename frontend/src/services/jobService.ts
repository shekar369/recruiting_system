import api from './api'

export interface Job {
  id?: string
  title: string
  description?: string
  department?: string
  location?: string
  employment_type?: string
  work_mode?: string
  salary_min?: number
  salary_max?: number
  currency?: string
  required_skills?: string[]
  preferred_skills?: string[]
  experience_min?: number
  experience_max?: number
  education_level?: string
  responsibilities?: string[]
  benefits?: string[]
  status?: string
  priority?: string
  posted_by?: string
  number_of_openings?: number
  application_deadline?: string
  created_at?: string
  updated_at?: string
  posted_at?: string
  closed_at?: string
}

export interface JobListResponse {
  total: number
  page: number
  size: number
  jobs: Job[]
}

export const jobService = {
  getAll: async (page: number = 1, size: number = 10) => {
    const response = await api.get<JobListResponse>('/api/v1/jobs', {
      params: { page, size }
    })
    return response.data
  },

  getById: async (id: string) => {
    const response = await api.get(`/api/v1/jobs/${id}`)
    return response.data
  },

  create: async (job: Job) => {
    const response = await api.post('/api/v1/jobs', job)
    return response.data
  },

  update: async (id: string, job: Partial<Job>) => {
    const response = await api.put(`/api/v1/jobs/${id}`, job)
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(`/api/v1/jobs/${id}`)
    return response.data
  },

  matchCandidates: async (jobId: string) => {
    const response = await api.post(`/api/v1/jobs/${jobId}/match`)
    return response.data
  },

  getRecommendations: async (jobId: string) => {
    const response = await api.get(`/api/v1/jobs/${jobId}/recommendations`)
    return response.data
  }
}
