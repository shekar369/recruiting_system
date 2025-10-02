import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Candidate {
  id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  location?: string
}

interface CandidatesState {
  candidates: Candidate[]
  selectedCandidate: Candidate | null
  loading: boolean
  error: string | null
}

const initialState: CandidatesState = {
  candidates: [],
  selectedCandidate: null,
  loading: false,
  error: null,
}

const candidatesSlice = createSlice({
  name: 'candidates',
  initialState,
  reducers: {
    setCandidates: (state, action: PayloadAction<Candidate[]>) => {
      state.candidates = action.payload
    },
    setSelectedCandidate: (state, action: PayloadAction<Candidate | null>) => {
      state.selectedCandidate = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setCandidates, setSelectedCandidate, setLoading, setError } = candidatesSlice.actions
export default candidatesSlice.reducer
