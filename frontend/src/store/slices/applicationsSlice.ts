import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Application {
  id: string
  candidate_id: string
  job_id: string
  status: string
  applied_at: string
}

interface ApplicationsState {
  applications: Application[]
  selectedApplication: Application | null
  loading: boolean
  error: string | null
}

const initialState: ApplicationsState = {
  applications: [],
  selectedApplication: null,
  loading: false,
  error: null,
}

const applicationsSlice = createSlice({
  name: 'applications',
  initialState,
  reducers: {
    setApplications: (state, action: PayloadAction<Application[]>) => {
      state.applications = action.payload
    },
    setSelectedApplication: (state, action: PayloadAction<Application | null>) => {
      state.selectedApplication = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setApplications, setSelectedApplication, setLoading, setError } = applicationsSlice.actions
export default applicationsSlice.reducer
