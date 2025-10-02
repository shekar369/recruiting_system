import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Job {
  id: string
  title: string
  department?: string
  location?: string
  employment_type?: string
  status: string
}

interface JobsState {
  jobs: Job[]
  selectedJob: Job | null
  loading: boolean
  error: string | null
}

const initialState: JobsState = {
  jobs: [],
  selectedJob: null,
  loading: false,
  error: null,
}

const jobsSlice = createSlice({
  name: 'jobs',
  initialState,
  reducers: {
    setJobs: (state, action: PayloadAction<Job[]>) => {
      state.jobs = action.payload
    },
    setSelectedJob: (state, action: PayloadAction<Job | null>) => {
      state.selectedJob = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setJobs, setSelectedJob, setLoading, setError } = jobsSlice.actions
export default jobsSlice.reducer
