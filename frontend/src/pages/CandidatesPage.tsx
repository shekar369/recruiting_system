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
import { candidateService, Candidate } from '../services/candidateService'

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
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
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [formData, setFormData] = useState<Partial<Candidate>>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    location: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    years_of_experience: undefined,
    current_job_title: '',
    current_company: '',
    expected_salary_min: undefined,
    expected_salary_max: undefined,
    currency: 'USD',
    availability: 'immediate',
    status: 'active',
    source: '',
    notes: '',
  })

  const fetchCandidates = async () => {
    try {
      setLoading(true)
      const response = await candidateService.getAll(page + 1, rowsPerPage)
      setCandidates(response.candidates || [])
      setTotal(response.total || 0)
      setError(null)
    } catch (err: any) {
      console.error('Error fetching candidates:', err)
      setError(err.response?.data?.detail || 'Failed to load candidates')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCandidates()
  }, [page, rowsPerPage])

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleOpenDialog = (mode: 'add' | 'edit' | 'view', candidate?: Candidate) => {
    setDialogMode(mode)
    if (candidate) {
      setSelectedCandidate(candidate)
      setFormData(candidate)
    } else {
      setSelectedCandidate(null)
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        location: '',
        linkedin_url: '',
        github_url: '',
        portfolio_url: '',
        years_of_experience: undefined,
        current_job_title: '',
        current_company: '',
        expected_salary_min: undefined,
        expected_salary_max: undefined,
        currency: 'USD',
        availability: 'immediate',
        status: 'active',
        source: '',
        notes: '',
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setSelectedCandidate(null)
    setFormData({})
  }

  const handleInputChange = (field: keyof Candidate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      if (dialogMode === 'add') {
        await candidateService.create(formData as Candidate)
        setSuccess('Candidate created successfully')
      } else if (dialogMode === 'edit' && selectedCandidate) {
        await candidateService.update(selectedCandidate.id!, formData)
        setSuccess('Candidate updated successfully')
      }
      handleCloseDialog()
      fetchCandidates()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save candidate')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      try {
        await candidateService.delete(id)
        setSuccess('Candidate deleted successfully')
        fetchCandidates()
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to delete candidate')
      }
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active': return 'success'
      case 'inactive': return 'default'
      case 'hired': return 'primary'
      case 'blacklisted': return 'error'
      default: return 'default'
    }
  }

  if (loading && candidates.length === 0) {
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
            Candidates
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and track all candidates
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('add')}
        >
          Add Candidate
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
            placeholder="Search candidates..."
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
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Experience</TableCell>
              <TableCell>Current Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {candidates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 5 }}>
                  <Typography color="text.secondary">
                    No candidates found. Click "Add Candidate" to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              candidates.map((candidate) => (
                <TableRow key={candidate.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {candidate.first_name} {candidate.last_name}
                    </Typography>
                  </TableCell>
                  <TableCell>{candidate.email}</TableCell>
                  <TableCell>{candidate.phone || '-'}</TableCell>
                  <TableCell>{candidate.location || '-'}</TableCell>
                  <TableCell>
                    {candidate.years_of_experience
                      ? `${candidate.years_of_experience} years`
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {candidate.current_job_title ? (
                      <Box>
                        <Typography variant="body2">
                          {candidate.current_job_title}
                        </Typography>
                        {candidate.current_company && (
                          <Typography variant="caption" color="text.secondary">
                            at {candidate.current_company}
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={candidate.status || 'active'}
                      color={getStatusColor(candidate.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('view', candidate)}
                    >
                      <VisibilityIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('edit', candidate)}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(candidate.id!)}
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
              {dialogMode === 'add' ? 'Add Candidate' : dialogMode === 'edit' ? 'Edit Candidate' : 'View Candidate'}
            </Typography>
            <IconButton onClick={handleCloseDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="First Name"
                value={formData.first_name || ''}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                required
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={formData.last_name || ''}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                required
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone || ''}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location || ''}
                onChange={(e) => handleInputChange('location', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Current Job Title"
                value={formData.current_job_title || ''}
                onChange={(e) => handleInputChange('current_job_title', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Current Company"
                value={formData.current_company || ''}
                onChange={(e) => handleInputChange('current_company', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Years of Experience"
                type="number"
                value={formData.years_of_experience || ''}
                onChange={(e) => handleInputChange('years_of_experience', parseInt(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Availability</InputLabel>
                <Select
                  value={formData.availability || 'immediate'}
                  onChange={(e) => handleInputChange('availability', e.target.value)}
                  label="Availability"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="immediate">Immediate</MenuItem>
                  <MenuItem value="2weeks">2 Weeks</MenuItem>
                  <MenuItem value="1month">1 Month</MenuItem>
                  <MenuItem value="2months">2 Months</MenuItem>
                  <MenuItem value="3months">3+ Months</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Min Expected Salary"
                type="number"
                value={formData.expected_salary_min || ''}
                onChange={(e) => handleInputChange('expected_salary_min', parseFloat(e.target.value))}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Max Expected Salary"
                type="number"
                value={formData.expected_salary_max || ''}
                onChange={(e) => handleInputChange('expected_salary_max', parseFloat(e.target.value))}
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
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="LinkedIn URL"
                value={formData.linkedin_url || ''}
                onChange={(e) => handleInputChange('linkedin_url', e.target.value)}
                placeholder="https://linkedin.com/in/..."
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="GitHub URL"
                value={formData.github_url || ''}
                onChange={(e) => handleInputChange('github_url', e.target.value)}
                placeholder="https://github.com/..."
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Portfolio URL"
                value={formData.portfolio_url || ''}
                onChange={(e) => handleInputChange('portfolio_url', e.target.value)}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status || 'active'}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  label="Status"
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="hired">Hired</MenuItem>
                  <MenuItem value="blacklisted">Blacklisted</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Source"
                value={formData.source || ''}
                onChange={(e) => handleInputChange('source', e.target.value)}
                placeholder="e.g., LinkedIn, Referral, Job Board"
                disabled={dialogMode === 'view'}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Notes"
                value={formData.notes || ''}
                onChange={(e) => handleInputChange('notes', e.target.value)}
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
