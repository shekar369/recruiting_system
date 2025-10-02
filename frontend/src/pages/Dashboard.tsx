import { useEffect, useState } from 'react'
import { Box, Grid, Paper, Typography, CircularProgress, Alert } from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import WorkIcon from '@mui/icons-material/Work'
import AssignmentIcon from '@mui/icons-material/Assignment'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import { candidateService } from '../services/candidateService'
import { jobService } from '../services/jobService'

interface Stats {
  totalCandidates: number
  activeJobs: number
  totalApplications: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    totalCandidates: 0,
    activeJobs: 0,
    totalApplications: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const [candidatesRes, jobsRes] = await Promise.all([
          candidateService.getAll(1, 1),
          jobService.getAll(1, 1, 'active'),
        ])

        setStats({
          totalCandidates: candidatesRes.total || 0,
          activeJobs: jobsRes.total || 0,
          totalApplications: 0, // Will be implemented later
        })
        setError(null)
      } catch (err: any) {
        console.error('Error fetching stats:', err)
        setError(err.message || 'Failed to load dashboard stats')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
        Welcome to the RAG Recruiting System
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3,
              }
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: 'primary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <PeopleIcon color="primary" sx={{ fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Candidates
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.totalCandidates}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3,
              }
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: 'success.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <WorkIcon color="success" sx={{ fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Active Jobs
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.activeJobs}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3,
              }
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: 'warning.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AssignmentIcon color="warning" sx={{ fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Applications
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.totalApplications}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3,
              }
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: 'info.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <TrendingUpIcon color="info" sx={{ fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Match Rate
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                0%
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, minHeight: 300 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography color="text.secondary">
              No recent activity
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, minHeight: 300 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Typography color="text.secondary">
              Coming soon...
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
