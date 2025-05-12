# Authentication Features

## Overview
This branch implements user authentication using Supabase Auth, including signup, login, and password recovery functionality.

## Features

### User Authentication
- Email/password authentication
- Email confirmation flow
- Password reset functionality
- Session management
- Protected routes

### Email Templates
Custom email templates for:
- Account confirmation (`confirmation.html`)
- Password recovery (`recovery.html`)

## Implementation Details

### Session Management
```python
# app/dependencies.py
async def get_current_user(request: Request):
    # Retrieves user session from Supabase
    # Returns user data including id, email, and display_name
```

### Authentication Routes
```python
# app/routers/auth.py
@router.post("/signup")
async def signup(request: Request, email: str, password: str, name: str):
    # Handles user registration
    # Stores user metadata (display_name)
    # Sends confirmation email

@router.post("/login")
async def login(request: Request, email: str, password: str):
    # Handles user authentication
    # Stores session tokens
    # Redirects to home page

@router.get("/logout")
async def logout(request: Request):
    # Clears session
    # Signs out user
```

### Session Storage
- Access token and refresh token stored in request session
- Session middleware enabled for persistent authentication
- Secure token handling

## Email Configuration
Supabase email settings in `supabase/config.toml`:
```toml
[auth.email]
enable_signup = true
enable_confirmations = true
```

## Test Data
When running locally, the following test user is available:
- Email: test@example.com
- Password: password

## Security Features
- Password hashing (handled by Supabase)
- Session token management
- CSRF protection
- Secure password reset flow
- Email confirmation requirement

## UI Components
- Login form with error handling
- Signup form with validation
- User session display in navigation
- Responsive authentication pages

## Error Handling
- Invalid credentials
- Email already in use
- Session expiration
- Network errors
- Form validation

## Dependencies
- FastAPI
- Supabase Python Client
- Jinja2 Templates
- Session Middleware

## Future Improvements
- Social authentication (Google, GitHub, etc.)
- Remember me functionality
- Two-factor authentication
- Account deletion
- Session timeout configuration 