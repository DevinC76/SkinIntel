# Authentication API Documentation

Complete guide to using SkinIntel's authentication endpoints powered by Supabase.

## Table of Contents

- [Overview](#overview)
- [Authentication Flow](#authentication-flow)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Rate Limits](#rate-limits)

## Overview

SkinIntel uses **Supabase Authentication** with JWT (JSON Web Tokens) for secure user authentication. All analysis endpoints require a valid access token.

### Token Types

- **Access Token**: Short-lived token (default: 1 hour) used for API requests
- **Refresh Token**: Long-lived token used to obtain new access tokens

### Security Features

- ✅ JWT-based authentication
- ✅ Secure password hashing (bcrypt)
- ✅ Email verification (optional)
- ✅ Rate limiting on auth endpoints
- ✅ Row Level Security (RLS) in database

## Authentication Flow

```
┌─────────┐                                    ┌─────────┐
│  Client │                                    │  Server │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  POST /auth/signup                           │
     │  { email, password }                         │
     ├─────────────────────────────────────────────▶│
     │                                              │
     │  ◀─────── { user_id, message } ─────────────┤
     │                                              │
     │  POST /auth/login                            │
     │  { email, password }                         │
     ├─────────────────────────────────────────────▶│
     │                                              │
     │  ◀─── { access_token, refresh_token } ──────┤
     │                                              │
     │  POST /skinprocessing                        │
     │  Authorization: Bearer <access_token>        │
     ├─────────────────────────────────────────────▶│
     │                                              │
     │  ◀─────────── { analysis_data } ────────────┤
     │                                              │
```

## Endpoints

### 1. Sign Up

Create a new user account.

**Endpoint:** `POST /auth/signup`

**Rate Limit:** 5 requests per minute

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Validation Rules:**
- Email must be valid format
- Password must be at least 6 characters

**Success Response (200):**
```json
{
  "message": "User created successfully. Please check your email to verify your account.",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Email already exists | User with this email is already registered |
| 400 | Invalid email format | Email format is invalid |
| 400 | Password too short | Password must be at least 6 characters |
| 429 | Rate limit exceeded | Too many signup attempts |

---

### 2. Login

Authenticate and receive access tokens.

**Endpoint:** `POST /auth/login`

**Rate Limit:** 10 requests per minute

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "v1.MjQxNzY4MzI4MA.gF8Dh...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

**Token Details:**
- `access_token`: Use this in Authorization header for API requests
- `refresh_token`: Use to get new access token when current expires
- `expires_in`: Seconds until access token expires (default: 3600 = 1 hour)

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Invalid credentials | Email or password is incorrect |
| 401 | Email not confirmed | User hasn't verified their email |
| 429 | Rate limit exceeded | Too many login attempts |

---

### 3. Logout

Invalidate current session.

**Endpoint:** `POST /auth/logout`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Invalid or expired token | Token is invalid or expired |
| 500 | Logout failed | Server error during logout |

---

### 4. Refresh Token

Get a new access token using refresh token.

**Endpoint:** `POST /auth/refresh`

**Rate Limit:** 20 requests per minute

**Request Body:**
```json
{
  "refresh_token": "v1.MjQxNzY4MzI4MA.gF8Dh..."
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "v1.MjQxNzY4MzI4MA.new_token...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Invalid refresh token | Refresh token is invalid or expired |
| 429 | Rate limit exceeded | Too many refresh attempts |

---

### 5. Get Current User

Get information about the authenticated user.

**Endpoint:** `GET /me`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Invalid or expired token | Token is invalid or expired |

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- **200** - Success
- **400** - Bad Request (validation error)
- **401** - Unauthorized (invalid/expired token or wrong credentials)
- **429** - Too Many Requests (rate limit exceeded)
- **500** - Internal Server Error

## Examples

### Example 1: Complete Sign Up & Login Flow

```bash
# 1. Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "mySecurePassword123"
  }'

# Response:
# {
#   "message": "User created successfully. Please check your email to verify your account.",
#   "user_id": "550e8400-e29b-41d4-a716-446655440000"
# }

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "mySecurePassword123"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "v1.MjQxNzY4MzI4MA...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }
```

### Example 2: Using Access Token

```bash
# Store the access token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Make authenticated request
curl -X POST http://localhost:8000/skinprocessing \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@skin_image.jpg"
```

### Example 3: Refreshing Token

```bash
# When access token expires, use refresh token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "v1.MjQxNzY4MzI4MA..."
  }'

# Response includes new access token and refresh token
```

### Example 4: JavaScript/TypeScript (Frontend)

```typescript
// Sign up
async function signup(email: string, password: string) {
  const response = await fetch('http://localhost:8000/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail)
  }

  return response.json()
}

// Login
async function login(email: string, password: string) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail)
  }

  const data = await response.json()

  // Store tokens
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)

  return data
}

// Make authenticated request
async function analyzeImage(file: File) {
  const token = localStorage.getItem('access_token')

  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('http://localhost:8000/skinprocessing', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })

  if (response.status === 401) {
    // Token expired, refresh it
    await refreshToken()
    // Retry request
    return analyzeImage(file)
  }

  return response.json()
}

// Refresh token
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token')

  const response = await fetch('http://localhost:8000/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  })

  const data = await response.json()

  // Update stored tokens
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
}
```

### Example 5: Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

class SkinIntelClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None

    def signup(self, email: str, password: str):
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()

    def login(self, email: str, password: str):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]

        return data

    def analyze_image(self, image_path: str):
        with open(image_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Bearer {self.access_token}'}

            response = requests.post(
                f"{BASE_URL}/skinprocessing",
                files=files,
                headers=headers
            )

            if response.status_code == 401:
                # Token expired, refresh
                self.refresh_access_token()
                # Retry
                return self.analyze_image(image_path)

            response.raise_for_status()
            return response.json()

    def refresh_access_token(self):
        response = requests.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]

        return data

# Usage
client = SkinIntelClient()
client.signup("user@example.com", "password123")
client.login("user@example.com", "password123")
result = client.analyze_image("skin_photo.jpg")
print(result)
```

## Rate Limits

Rate limits are applied per IP address.

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/signup` | 5 requests | 1 minute |
| `/auth/login` | 10 requests | 1 minute |
| `/auth/refresh` | 20 requests | 1 minute |

When rate limit is exceeded, you'll receive:

```json
{
  "detail": "Rate limit exceeded"
}
```

**HTTP Status:** 429 Too Many Requests

**Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
```

## Best Practices

1. **Store Tokens Securely**
   - Never expose tokens in client-side code
   - Use httpOnly cookies when possible
   - Store in secure storage (not localStorage for sensitive apps)

2. **Handle Token Expiration**
   - Implement automatic token refresh
   - Gracefully handle 401 errors
   - Redirect to login when refresh fails

3. **Password Requirements**
   - Minimum 6 characters (recommended: 12+)
   - Include mix of letters, numbers, symbols
   - Don't store passwords client-side

4. **Error Handling**
   - Always check response status
   - Parse error messages from `detail` field
   - Provide user-friendly error messages

5. **Rate Limiting**
   - Implement exponential backoff on failures
   - Don't spam auth endpoints
   - Cache tokens appropriately

## Security Notes

⚠️ **Important Security Considerations:**

- Always use HTTPS in production
- Access tokens expire after 1 hour
- Refresh tokens are rotated on each use
- Never share tokens between users
- Clear tokens on logout
- Validate email/password on client before sending
- Row Level Security (RLS) ensures users only access their own data

## Troubleshooting

### "Invalid credentials" error
- Check email and password are correct
- Ensure email is verified (if verification is enabled)
- Check for extra whitespace in inputs

### "Invalid or expired token"
- Token may have expired (1 hour default)
- Use refresh token to get new access token
- Re-login if refresh token also expired

### "Rate limit exceeded"
- Wait 60 seconds before retrying
- Implement exponential backoff
- Check for infinite retry loops in code

### "Email already exists"
- User has already signed up
- Use password reset flow instead
- Try logging in

---

For more information, see the [main README](../README.md) or check the [API documentation](http://localhost:8000/docs) when running the server.
