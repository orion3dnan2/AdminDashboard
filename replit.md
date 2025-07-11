# BaytAlSudani Admin Dashboard

## Overview

BaytAlSudani is a Flask-based web application providing administrative and merchant dashboards for a Sudanese marketplace platform. The application serves as a management interface for an existing API backend, offering Arabic-language RTL (Right-to-Left) support for managing users, stores, products, services, ads, jobs, and orders.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Framework**: Bootstrap 5 RTL for Arabic language support
- **Language Support**: Arabic (RTL) with proper typography using Tajawal font
- **Client-Side**: Vanilla JavaScript with Bootstrap components
- **Styling**: Custom CSS with Arabic-first design principles

### Backend Architecture
- **Web Framework**: Flask with Blueprint-based modular architecture
- **Session Management**: Flask sessions for authentication state
- **API Integration**: HTTP client-based communication with external API
- **Authentication**: Decorator-based authorization system
- **Error Handling**: Centralized error handling with Arabic error messages

### Data Flow Architecture
- **API Client Pattern**: Centralized API communication through dedicated client class
- **Session-Based Auth**: User authentication state stored in Flask sessions
- **Request-Response Flow**: Standard HTTP request/response cycle with API backend
- **Template Rendering**: Server-side rendering with Jinja2 templates

## Key Components

### Authentication System
- **Admin Authentication**: Username/password login with session management
- **Merchant Authentication**: Email/password login with store association
- **Authorization Decorators**: `@admin_required` and `@merchant_required` for route protection
- **Session Management**: Centralized session handling for user state

### Blueprint Architecture
- **Admin Blueprint**: Complete administrative interface (`/admin` routes)
- **Merchant Blueprint**: Merchant-specific functionality (`/merchant` routes)
- **Modular Design**: Separated concerns with dedicated route handlers

### API Client Integration
- **Centralized Communication**: Single `APIClient` class for all backend interactions
- **Error Handling**: Consistent error response handling with Arabic messages
- **Request Management**: Session-based HTTP client with proper headers
- **Timeout Configuration**: 30-second timeout for API requests

### Template System
- **Base Template**: Shared layout with Bootstrap RTL and Arabic fonts
- **Component Templates**: Modular templates for different sections
- **Responsive Design**: Mobile-first approach with Bootstrap grid system
- **Accessibility**: Arabic language support with proper RTL layout

## Data Flow

### Authentication Flow
1. User submits login credentials through form
2. Flask route validates input and calls API client
3. API client authenticates with external backend
4. Session stores user information on successful login
5. Decorators protect subsequent requests

### Data Management Flow
1. Protected routes require valid session
2. API client fetches data from external backend
3. Templates render data with Arabic localization
4. User interactions trigger API calls through forms
5. Results displayed with appropriate Arabic messaging

### Error Handling Flow
1. API errors captured by client class
2. Arabic error messages generated based on status codes
3. Flash messages display user-friendly notifications
4. Fallback routes handle 404/500 errors

## External Dependencies

### Required Services
- **External API Backend**: Primary data source at `API_BASE_URL` environment variable
- **Session Storage**: Flask session management requires secret key

### Third-Party Libraries
- **Flask**: Core web framework
- **Requests**: HTTP client for API communication
- **Werkzeug**: WSGI utilities and proxy fix
- **Bootstrap 5 RTL**: UI framework with Arabic support
- **Font Awesome**: Icon library
- **Google Fonts**: Tajawal font for Arabic typography

### Environment Configuration
- `API_BASE_URL`: Backend API endpoint (defaults to localhost:8000)
- `SESSION_SECRET`: Flask session encryption key

## Deployment Strategy

### Application Entry Points
- **Main Application**: `app.py` contains Flask app configuration
- **Development Server**: `main.py` provides development entry point
- **WSGI Configuration**: ProxyFix middleware for reverse proxy support

### Static Asset Management
- **CSS**: Custom Arabic-RTL styles in `static/css/style.css`
- **JavaScript**: Enhanced functionality in `static/js/main.js`
- **Template Assets**: Bootstrap and Font Awesome loaded from CDN

### Security Considerations
- **Session Security**: Configurable session secret key
- **CSRF Protection**: Form-based submissions (can be enhanced)
- **Input Validation**: Client-side and server-side validation
- **Error Sanitization**: Safe error message display

### Scalability Design
- **Stateless Backend**: API client doesn't maintain state
- **Session-Based Auth**: Can be moved to external store if needed
- **Modular Architecture**: Easy to extend with additional blueprints
- **CDN Integration**: Static assets served from external CDNs

The application follows a clean separation of concerns with the Flask frontend serving as a presentation layer for the existing BaytAlSudani API backend, providing a localized Arabic interface for platform administration.