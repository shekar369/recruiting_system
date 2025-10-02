import { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Snackbar,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import SearchIcon from '@mui/icons-material/Search'
import VisibilityIcon from '@mui/icons-material/Visibility'
import CloseIcon from '@mui/icons-material/Close'
import { jobService, Job } from '../services/jobService'

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [total, setTotal] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')

  // Dialog states
  const [openDialog, setOpenDialog] = useState(false)
  const [dialogMode, setDialogMode] = useState<'add' | 'edit' | 'view'>('add')
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [formData, setFormData] = useState<Partial<Job>>({
    title: '',
    description: '',
    department: '',
    location: '',
    employment_type: 'full-time',
    work_mode: 'onsite',
    salary_min: undefined,
    salary_max: undefined,
    currency: 'USD',
    experience_min: undefined,
    experience_max: undefined,
    education_level: '',
    status: 'draft',
    priority: 'medium',
    number_of_openings: 1,
  })

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await jobService.getAll(page + 1, rowsPerPage)
      setJobs(response.jobs || [])
      setTotal(response.total || 0)
      setError(null)
    } catch (err: any) {
      console.error('Error fetching jobs:', err)
      setError(err.response?.data?.detail || 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [page, rowsPerPage])

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleOpenDialog = (mode: 'add' | 'edit' | 'view', job?: Job) => {
    setDialogMode(mode)
    if (job) {
      setSelectedJob(job)
      setFormData(job)
    } else {
      setSelectedJob(null)
      setFormData({
        title: '',
        description: '',
        department: '',
        location: '',
        employment_type: 'full-time',
        work_mode: 'onsite',
        salary_min: undefined,
        salary_max: undefined,
        currency: 'USD',
        experience_min: undefined,
        experience_max: undefined,
        education_level: '',
        status: 'draft',
        priority: 'medium',
        number_of_openings: 1,
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedJob(null)
    setFormData({})
  }

  const handleInputChange = (field: keyof Job, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      if (dialogMode === 'add') {
        await jobService.create(formData as Job)
        setSuccess('Job created successfully')
      } else if (dialogMode === 'edit' && selectedJob) {
        await jobService.update(selectedJob.id!, formData)
        setSuccess('Job updated successfully')
      }
      handleCloseDialog()
      fetchJobs()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save job')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        await jobService.delete(id)
        setSuccess('Job deleted successfully')
        fetchJobs()
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to delete job')
      }
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active': return 'success'
      case 'draft': return 'default'
      case 'closed': return 'error'
      case 'on_hold': return 'warning'
      default: return 'default'
    }
  }

  const getEmploymentTypeColor = (type?: string) => {
    switch (type) {
      case 'full-time': return 'primary'
      case 'part-time': return 'secondary'
      case 'contract': return 'info'
      case 'internship': return 'warning'
      default: return 'default'
    }
  }

  if (loading && jobs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <div>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Jobs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage job postings and track applications
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('add')}
        >
          Post New Job
        </Button>
      </Box>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
        message={success}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 2 }}>
        <Box p={2}>
          <TextField
            fullWidth
            placeholder="Search jobs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Experience</TableCell>
              <TableCell>Openings</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 5 }}>
                  <Typography color="text.secondary">
                    No jobs found. Click "Post New Job" to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              jobs.map((job) => (
                <TableRow key={job.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {job.title}
                    </Typography>
                    {job.work_mode && (
                      <Typography variant="caption" color="text.secondary">
                        {job.work_mode}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{job.department || '-'}</TableCell>
                  <TableCell>{job.location || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={job.employment_type || 'full-time'}
                      color={getEmploymentTypeColor(job.employment_type)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {job.experience_min && job.experience_max
                      ? `${job.experience_min}-${job.experience_max} years`
                      : job.experience_min
                      ? `${job.experience_min}+ years`
                      : '-'}
                  </TableCell>
                  <TableCell>{job.number_of_openings || 1}</TableCell>
                  <TableCell>
                    <Chip
                      label={job.status || 'draft'}
                      color={getStatusColor(job.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('view', job)}
                    >
                      <VisibilityIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('edit', job)}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(job.id!)}
                      color="error"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Add/Edit/View Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {dialogMode === 'add' ? 'Post New Job' : dialogMode === 'edit' ? 'Edit Job' : 'View Job'}
            </Typography>
            <IconButton onClick={handleCloseDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Job Title"
                value={formData.title || ''}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Department"
                value={formData.department || ''}
                onChange={(e) => handleInputChange('department', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location || ''}
                onChange={(e) => handleInputChange('location', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Employment Type</InputLabel>
                <Select
                  value={formData.employment_type || 'full-time'}
                  onChange={(e) => handleInputChange('employment_type', e.target.value)}
                  label="Employment Type"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="full-time">Full-time</MenuItem>
                  <MenuItem value="part-time">Part-time</MenuItem>
                  <MenuItem value="contract">Contract</MenuItem>
                  <MenuItem value="internship">Internship</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Work Mode</InputLabel>
                <Select
                  value={formData.work_mode || 'onsite'}
                  onChange={(e) => handleInputChange('work_mode', e.target.value)}
                  label="Work Mode"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="remote">Remote</MenuItem>
                  <MenuItem value="hybrid">Hybrid</MenuItem>
                  <MenuItem value="onsite">Onsite</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Min Salary"
                type="number"
                value={formData.salary_min || ''}
                onChange={(e) => handleInputChange('salary_min', parseFloat(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Max Salary"
                type="number"
                value={formData.salary_max || ''}
                onChange={(e) => handleInputChange('salary_max', parseFloat(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={formData.currency || 'USD'}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                  label="Currency"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="USD">USD</MenuItem>
                  <MenuItem value="EUR">EUR</MenuItem>
                  <MenuItem value="GBP">GBP</MenuItem>
                  <MenuItem value="INR">INR</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Min Experience (years)"
                type="number"
                value={formData.experience_min || ''}
                onChange={(e) => handleInputChange('experience_min', parseInt(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Experience (years)"
                type="number"
                value={formData.experience_max || ''}
                onChange={(e) => handleInputChange('experience_max', parseInt(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Education Level"
                value={formData.education_level || ''}
                onChange={(e) => handleInputChange('education_level', e.target.value)}
                placeholder="e.g., Bachelor's, Master's"
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Number of Openings"
                type="number"
                value={formData.number_of_openings || 1}
                onChange={(e) => handleInputChange('number_of_openings', parseInt(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status || 'draft'}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  label="Status"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="on_hold">On Hold</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority || 'medium'}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  label="Priority"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                value={formData.description || ''}
                onChange={(e) => handleInputChange('description', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          {dialogMode !== 'view' && (
            <Button onClick={handleSubmit} variant="contained" disabled={loading}>
              {dialogMode === 'add' ? 'Create' : 'Update'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}
