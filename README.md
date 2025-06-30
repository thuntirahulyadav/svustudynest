# SVUSTUDYNEST - WHERE YOU ALL STUDY REASOURCE AT ONE PLACE

## Overview
SVUSTUDYNEST is a comprehensive study hub for Sri Venkateswara University students. The application now includes a robust authentication system that ensures only logged-in users can access the educational content.

## Authentication Features

### 🔐 Secure Login System
- **Session Management**: 24-hour session duration with automatic expiration
- **Persistent Login**: Users stay logged in across browser sessions until session expires
- **Automatic Redirects**: Users are automatically redirected to appropriate pages based on authentication status

### 🛡️ Security Measures
- **Multi-factor Authentication Check**: Validates student name, roll number, login time, and authentication status
- **Periodic Validation**: Authentication is checked every 5 minutes to ensure session validity
- **Automatic Logout**: Sessions expire after 24 hours or when user clicks logout
- **Storage Cleanup**: All authentication data is cleared on logout or session expiration

### 🚪 Access Control
- **Protected Pages**: All educational content pages require authentication
- **Login Required**: Users must log in before accessing any content
- **Seamless Navigation**: Authenticated users can navigate freely between pages

## File Structure

### Core Files
- `index.html` - Entry point that redirects based on authentication status
- `login.html` - Login page with enhanced session management
- `auth.js` - Common authentication script used by all protected pages
- `dashboard.html` - Main dashboard (requires authentication)
- `semester4.html` - Semester 4 subjects page (requires authentication)
- `os.html` - Operating System subject page (requires authentication)
- `os_unit1.html` - Unit 1 content page (requires authentication)

### Authentication Flow
1. **Entry Point**: `index.html` checks authentication and redirects accordingly
2. **Login**: `login.html` handles user authentication and stores session data
3. **Protected Pages**: All content pages include `auth.js` for authentication checks
4. **Logout**: Users can logout from any page, clearing all session data

## How to Use

### For Students
1. **Access**: Navigate to the application (starts at `index.html`)
2. **Login**: Enter your roll number and password
3. **Browse**: Access all educational content freely
4. **Logout**: Click the logout button when finished

### For Developers
1. **Add New Pages**: Include `auth.js` script in any new HTML page
2. **Add Logout Button**: Include `<button id="logoutBtn">Logout</button>` in the navbar
3. **Add Student Name Display**: Include `<span id="studentName"></span>` in the navbar

## Technical Implementation

### Session Storage
The authentication system uses browser localStorage to store:
- `studentName`: Student's full name
- `studentRoll`: Student's roll number
- `loginTime`: Timestamp when user logged in
- `isAuthenticated`: Boolean flag indicating authentication status

### Authentication Check Function
```javascript
function checkAuthentication() {
  // Validates all required authentication data
  // Checks session expiration (24 hours)
  // Redirects to login if invalid
}
```

### Automatic Features
- **Session Validation**: Every 5 minutes
- **Auto-redirect**: Invalid sessions redirect to login
- **Cleanup**: Expired sessions clear all data

## Security Considerations

### Client-Side Security
- Session data stored in localStorage
- 24-hour session expiration
- Periodic validation checks
- Automatic cleanup on logout

### Recommended Server-Side Enhancements
- Implement server-side session validation
- Add JWT tokens for enhanced security
- Use HTTPS for all communications
- Implement rate limiting on login attempts

## Browser Compatibility
- Modern browsers with localStorage support
- JavaScript enabled required
- Responsive design for mobile and desktop

## Getting Started
1. Ensure the backend server is running (`app.py`)
2. Open `index.html` in a web browser
3. Login with valid student credentials
4. Navigate through the educational content

## Support
For technical support or questions about the authentication system, please refer to the backend documentation or contact the development team. 
