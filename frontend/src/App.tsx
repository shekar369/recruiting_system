import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/common/Layout'
import Dashboard from './pages/Dashboard'
import CandidatesPage from './pages/CandidatesPage'
import JobsPage from './pages/JobsPage'
import ApplicationsPage from './pages/ApplicationsPage'
import { LoginPage } from './pages/LoginPage'
import { ProfilePage } from './pages/ProfilePage'
import { authService } from './services/authService'

function App() {
  const location = useLocation()
  const isAuthenticated = authService.isAuthenticated()

  if (!isAuthenticated) {
    return <LoginPage />
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/applications" element={<ApplicationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Box>
  )
}

export default App
