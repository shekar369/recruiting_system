import { configureStore } from '@reduxjs/toolkit'
import candidatesReducer from './slices/candidatesSlice'
import jobsReducer from './slices/jobsSlice'
import applicationsReducer from './slices/applicationsSlice'

export const store = configureStore({
  reducer: {
    candidates: candidatesReducer,
    jobs: jobsReducer,
    applications: applicationsReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
