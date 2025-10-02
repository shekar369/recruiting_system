import { Box, Typography, Paper } from '@mui/material'

export default function ApplicationsPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Applications
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Applications will be displayed here</Typography>
      </Paper>
    </Box>
  )
}
