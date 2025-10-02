import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  Divider,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
} from '@mui/material';
import { PersonOutline, LockOutlined, Email, Badge } from '@mui/icons-material';
import { authService, User } from '../services/authService';

export const ProfilePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Profile update state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');

  // Password change state
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setFullName(userData.full_name || '');
      setEmail(userData.email);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const updated = await authService.updateProfile({
        full_name: fullName,
        email: email,
      });

      setUser(updated);
      setSuccess('Profile updated successfully');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    try {
      setPasswordError(null);

      if (newPassword !== confirmPassword) {
        setPasswordError('Passwords do not match');
        return;
      }

      if (newPassword.length < 8) {
        setPasswordError('Password must be at least 8 characters');
        return;
      }

      await authService.changePassword(oldPassword, newPassword);

      setShowPasswordDialog(false);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setSuccess('Password changed successfully');
    } catch (err: any) {
      setPasswordError(err.response?.data?.detail || 'Failed to change password');
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'recruiter':
        return 'primary';
      case 'hiring_manager':
        return 'secondary';
      default:
        return 'default';
    }
  };

  if (loading && !user) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  if (!user) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Failed to load user profile</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        User Profile
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Profile Information */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Avatar sx={{ width: 80, height: 80, mr: 2, bgcolor: 'primary.main' }}>
            <PersonOutline sx={{ fontSize: 40 }} />
          </Avatar>
          <Box>
            <Typography variant="h5">{user.username}</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip
                label={user.role}
                color={getRoleColor(user.role)}
                size="small"
              />
              {user.is_superuser && (
                <Chip label="Superuser" color="warning" size="small" />
              )}
              <Chip
                label={user.is_active ? 'Active' : 'Inactive'}
                color={user.is_active ? 'success' : 'default'}
                size="small"
              />
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              InputProps={{
                startAdornment: <Badge sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              InputProps={{
                startAdornment: <Email sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Username"
              value={user.username}
              disabled
              helperText="Username cannot be changed"
            />
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="contained"
              onClick={handleUpdateProfile}
              disabled={loading}
            >
              Update Profile
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Security Section */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Security
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Button
          variant="outlined"
          startIcon={<LockOutlined />}
          onClick={() => setShowPasswordDialog(true)}
        >
          Change Password
        </Button>

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Last Login: {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Account Created: {new Date(user.created_at).toLocaleString()}
          </Typography>
        </Box>
      </Paper>

      {/* Change Password Dialog */}
      <Dialog open={showPasswordDialog} onClose={() => setShowPasswordDialog(false)}>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          {passwordError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {passwordError}
            </Alert>
          )}

          <TextField
            fullWidth
            margin="normal"
            label="Current Password"
            type="password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
          />

          <TextField
            fullWidth
            margin="normal"
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            helperText="Minimum 8 characters, with uppercase, lowercase, and digit"
          />

          <TextField
            fullWidth
            margin="normal"
            label="Confirm New Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPasswordDialog(false)}>Cancel</Button>
          <Button onClick={handleChangePassword} variant="contained">
            Change Password
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
