# Authentication System Documentation

## Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `Admin123`
- Email: admin@example.com
- Role: Admin (Superuser)

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Public Endpoints

#### 1. Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin123"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### 2. Register New User
```
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "User Name",
  "role": "viewer"
}
```

**Available Roles:**
- `viewer` - Read-only access
- `hiring_manager` - Can view and manage jobs
- `recruiter` - Can manage candidates and applications
- `admin` - Full system access

### Protected Endpoints (Require Authentication)

Include the access token in the Authorization header:
```
Authorization: Bearer {access_token}
```

#### 3. Get Current User
```
GET /auth/me
```

#### 4. Update Current User
```
PUT /auth/me
Content-Type: application/json

{
  "full_name": "Updated Name",
  "email": "newemail@example.com"
}
```

#### 5. Change Password
```
POST /auth/change-password
Content-Type: application/json

{
  "old_password": "Admin123",
  "new_password": "NewSecurePass123"
}
```

#### 6. Refresh Token
```
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### Admin-Only Endpoints

#### 7. List All Users
```
GET /auth/users?skip=0&limit=100
```

#### 8. Get User by ID
```
GET /auth/users/{user_id}
```

#### 9. Update User (Admin)
```
PUT /auth/users/{user_id}
Content-Type: application/json

{
  "role": "recruiter",
  "is_active": true
}
```

#### 10. Delete User
```
DELETE /auth/users/{user_id}
```

## Token Information

- **Access Token**: Expires in 30 minutes
- **Refresh Token**: Expires in 7 days
- **Algorithm**: HS256 (HMAC with SHA-256)

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Using Postman or cURL

### Login Example (cURL)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}'
```

### Get Current User (cURL)
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Accessing from Frontend

The frontend should:
1. Store the access token (e.g., in localStorage or sessionStorage)
2. Include it in all API requests:
   ```javascript
   fetch('http://localhost:8000/api/v1/auth/me', {
     headers: {
       'Authorization': `Bearer ${accessToken}`
     }
   })
   ```
3. Refresh the token when it expires using the refresh token
4. Clear tokens on logout

## Role-Based Access Control

The system enforces a role hierarchy:
1. **Viewer** (Level 0) - Can only view data
2. **Hiring Manager** (Level 1) - Can manage jobs
3. **Recruiter** (Level 2) - Can manage candidates and applications
4. **Admin** (Level 3) - Full access to everything

Higher roles automatically have access to lower role permissions. Superusers bypass all role checks.

## Security Notes

- Default credentials should be changed immediately in production
- Store `SECRET_KEY` securely (currently in .env file)
- Use HTTPS in production
- Implement rate limiting for login attempts
- Consider adding 2FA for admin accounts
