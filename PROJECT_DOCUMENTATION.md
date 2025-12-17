# Project Documentation: AI Avatar Interview System

## Overview
This is a full-stack AI-powered interview system with customizable avatars, real-time video/audio processing, and intelligent question generation. The system consists of a FastAPI backend with MySQL database and a React frontend with WebRTC capabilities.

## Project Structure

### Root Directory
**Purpose:** Contains project configuration files, documentation, and quick-start scripts.

#### File: README.md
* **Purpose:** Main project documentation with setup instructions and feature overview.
* **Content Summary:** Comprehensive guide covering features, architecture, installation, API endpoints, database schema, deployment, and troubleshooting.
* **Key Technologies/Libraries Used:** Markdown, Documentation standards.

#### File: SETUP.md
* **Purpose:** Detailed setup guide with step-by-step installation instructions.
* **Content Summary:** Manual setup instructions, prerequisites, database configuration, environment variables, troubleshooting, and security considerations.
* **Key Technologies/Libraries Used:** Markdown, MySQL, Python, Node.js.

#### File: quick-start.bat
* **Purpose:** Windows batch script for automated project setup.
* **Content Summary:** Automated setup script for Windows users to quickly start the project.
* **Key Technologies/Libraries Used:** Windows Batch Scripting.

#### File: quick-start.sh
* **Purpose:** Unix/Linux/macOS shell script for automated project setup.
* **Content Summary:** Automated setup script for Unix-based systems to quickly start the project.
* **Key Technologies/Libraries Used:** Bash Shell Scripting.

---

## Backend Directory (`backend/`)

**Purpose:** FastAPI-based backend server providing REST API endpoints, database management, AI services, and business logic.

### File: backend/main.py
* **Purpose:** Main FastAPI application entry point and server configuration.
* **Content Summary:** Initializes FastAPI app with CORS middleware, includes all route modules, sets up database initialization, and configures server startup/shutdown events. Includes warning suppression for various AI libraries.
* **Key Technologies/Libraries Used:** FastAPI, Uvicorn, CORS Middleware, SQLAlchemy, Python warnings.

### File: backend/requirements.txt
* **Purpose:** Python dependencies specification for the backend.
* **Content Summary:** Lists all required Python packages including FastAPI, SQLAlchemy, AI libraries (Whisper, TTS, Transformers), authentication libraries, and database drivers.
* **Key Technologies/Libraries Used:** Python pip, FastAPI, SQLAlchemy, AI/ML libraries.

### File: backend/env.example
* **Purpose:** Template for environment variables configuration.
* **Content Summary:** Example environment file showing all required configuration variables for database, JWT, server settings, AI services, and file uploads.
* **Key Technologies/Libraries Used:** Environment variables, Configuration management.

---

### Folder: backend/app/
**Purpose:** Core application package containing database configuration, ORM models, and repository pattern implementation.

#### File: backend/app/__init__.py
* **Purpose:** Python package initialization file for the app module.
* **Content Summary:** Empty package initialization file with package description comment.
* **Key Technologies/Libraries Used:** Python package system.

#### File: backend/app/config.py
* **Purpose:** Application configuration management using Pydantic settings.
* **Content Summary:** Defines Settings class with database URL, JWT configuration, server settings, CORS configuration, file upload settings, AI services configuration, and Redis configuration. Includes property methods for list conversion.
* **Key Technologies/Libraries Used:** Pydantic Settings, Environment variables, Configuration management.

#### File: backend/app/db.py
* **Purpose:** Database connection and session management.
* **Content Summary:** Sets up async SQLAlchemy engine, session factory, and database initialization. Includes functions to create database if it doesn't exist, create tables, and manage database connections.
* **Key Technologies/Libraries Used:** SQLAlchemy, AsyncIO, MySQL, Alembic.

#### File: backend/app/orm_models.py
* **Purpose:** SQLAlchemy ORM models defining database schema.
* **Content Summary:** Defines all database tables including User, InterviewConfig, Question, Candidate, InterviewSession, Response, and Report models with proper relationships, constraints, and UUID primary keys.
* **Key Technologies/Libraries Used:** SQLAlchemy ORM, UUID, JSON fields, Foreign Keys, Relationships.

---

### Folder: backend/app/repositories/
**Purpose:** Data access layer implementing repository pattern for database operations.

#### File: backend/app/repositories/__init__.py
* **Purpose:** Repository package initialization and exports.
* **Content Summary:** Imports and exports all repository classes for easy access throughout the application.
* **Key Technologies/Libraries Used:** Python package system.

#### File: backend/app/repositories/user_repository.py
* **Purpose:** User data access operations.
* **Content Summary:** Implements CRUD operations for users including create, read, update, delete, authentication, and user existence checks. Uses async SQLAlchemy sessions and proper error handling.
* **Key Technologies/Libraries Used:** SQLAlchemy AsyncIO, Repository Pattern, Error Handling.

#### File: backend/app/repositories/candidate_repository.py
* **Purpose:** Candidate data access operations.
* **Content Summary:** Implements CRUD operations for candidates including creation, retrieval by ID/email, updates, deletion, resume path management, and candidate filtering by interview configuration.
* **Key Technologies/Libraries Used:** SQLAlchemy AsyncIO, Repository Pattern, File Management.

#### File: backend/app/repositories/interview_repository.py
* **Purpose:** Interview configuration data access operations.
* **Content Summary:** Manages interview configurations and questions including creation with shareable links, retrieval by ID or shareable link, updates, deletion, question management, and statistics tracking.
* **Key Technologies/Libraries Used:** SQLAlchemy AsyncIO, Repository Pattern, UUID generation.

#### File: backend/app/repositories/session_repository.py
* **Purpose:** Interview session data access operations.
* **Content Summary:** Handles interview session lifecycle including creation, retrieval, status updates, response management, and session statistics. Includes proper relationship loading and error handling.
* **Key Technologies/Libraries Used:** SQLAlchemy AsyncIO, Repository Pattern, Session Management.

#### File: backend/app/repositories/report_repository.py
* **Purpose:** Report data access operations.
* **Content Summary:** Manages interview reports including creation, retrieval by various criteria, updates, deletion, and statistical analysis like average scores and score ranges.
* **Key Technologies/Libraries Used:** SQLAlchemy AsyncIO, Repository Pattern, Statistical Analysis.

---

### Folder: backend/routes/
**Purpose:** API endpoint definitions using FastAPI routers.

#### File: backend/routes/__init__.py
* **Purpose:** Routes package initialization.
* **Content Summary:** Empty package initialization file with package description comment.
* **Key Technologies/Libraries Used:** Python package system.

#### File: backend/routes/auth.py
* **Purpose:** Authentication and user management endpoints.
* **Content Summary:** Implements user registration, login, token refresh, and current user retrieval. Includes JWT token generation, password hashing, and proper error handling with HTTP status codes.
* **Key Technologies/Libraries Used:** FastAPI, JWT, Password Hashing, OAuth2, HTTP Status Codes.

#### File: backend/routes/candidates.py
* **Content Summary:** Manages candidate operations including retrieval, updates, session management, resume uploads, and report generation. Includes file validation, upload handling, and comprehensive candidate reporting.
* **Key Technologies/Libraries Used:** FastAPI, File Upload, aiofiles, FormData, File Validation.

#### File: backend/routes/interviews.py
* **Purpose:** Interview configuration management endpoints.
* **Content Summary:** Handles interview creation, question generation, configuration management, and AI-powered question generation. Includes role-based access control and comprehensive error handling.
* **Key Technologies/Libraries Used:** FastAPI, AI Services, Role-based Access Control, Form Data.

#### File: backend/routes/admin.py
* **Purpose:** Administrative operations and system management.
* **Content Summary:** Provides user management, interview management, and system statistics for admin users. Includes CRUD operations for users and interviews with proper authorization.
* **Key Technologies/Libraries Used:** FastAPI, Admin Operations, System Statistics, Authorization.

#### File: backend/routes/ai.py
* **Purpose:** AI services endpoints for transcription and text-to-speech.
* **Content Summary:** Provides audio transcription, TTS generation, voice management, and AI services health checks. Integrates with various AI providers and includes proper error handling.
* **Key Technologies/Libraries Used:** FastAPI, AI Services, Audio Processing, File Response.

#### File: backend/routes/public.py
* **Purpose:** Public API endpoints for candidate access without authentication.
* **Content Summary:** Handles public interview access, candidate registration, session management, response submission, and interview completion. Includes file upload handling and comprehensive error management.
* **Key Technologies/Libraries Used:** FastAPI, Public API, File Upload, Session Management, FormData.

---

### Folder: backend/services/
**Purpose:** Business logic layer implementing core application services.

#### File: backend/services/__init__.py
* **Purpose:** Services package initialization.
* **Content Summary:** Empty package initialization file with package description comment.
* **Key Technologies/Libraries Used:** Python package system.

#### File: backend/services/ai_question_service.py
* **Purpose:** AI-powered interview question generation service.
* **Content Summary:** Implements question generation based on job roles, descriptions, focus areas, and difficulty levels. Includes template-based fallback system and follow-up question generation.
* **Key Technologies/Libraries Used:** Python, Template System, Random Selection, AI Question Generation.

#### File: backend/services/interview_service.py
* **Purpose:** Interview configuration business logic service.
* **Content Summary:** Manages interview configuration lifecycle including creation, updates, deletion, question management, and statistics. Implements factory pattern for service instantiation.
* **Key Technologies/Libraries Used:** Python, Factory Pattern, Business Logic, Service Layer.

#### File: backend/services/report_service.py
* **Purpose:** Interview report generation and analysis service.
* **Content Summary:** Generates comprehensive interview reports including score calculation, technical analysis, candidate evaluation, and report persistence. Implements sophisticated scoring algorithms.
* **Key Technologies/Libraries Used:** Python, Report Generation, Statistical Analysis, Scoring Algorithms.

#### File: backend/services/transcription_service.py
* **Purpose:** Audio transcription service supporting multiple providers.
* **Content Summary:** Provides audio-to-text conversion using Whisper (local/OpenAI), HuggingFace models. Includes segment extraction, language detection, and provider-specific implementations.
* **Key Technologies/Libraries Used:** Whisper, OpenAI API, HuggingFace Transformers, Audio Processing, AsyncIO.

#### File: backend/services/tts_service.py
* **Purpose:** Text-to-speech service supporting multiple providers.
* **Content Summary:** Converts text to speech using Coqui TTS or HuggingFace models. Includes voice management, audio file generation, and fallback mechanisms for Windows compatibility.
* **Key Technologies/Libraries Used:** Coqui TTS, HuggingFace Transformers, Audio Generation, Windows Compatibility.

---

### Folder: backend/models/
**Purpose:** Pydantic models for data validation and serialization.

#### File: backend/models/__init__.py
* **Purpose:** Models package initialization.
* **Content Summary:** Empty package initialization file with package description comment.
* **Key Technologies/Libraries Used:** Python package system.

#### File: backend/models/user.py
* **Purpose:** User-related Pydantic models and schemas.
* **Content Summary:** Defines user models including UserBase, UserCreate, UserUpdate, User, UserInDB, Token, TokenRefresh, and TokenData with proper validation and serialization.
* **Key Technologies/Libraries Used:** Pydantic, EmailStr, Enum, UUID, DateTime.

#### File: backend/models/candidate.py
* **Purpose:** Candidate-related Pydantic models and schemas.
* **Content Summary:** Defines candidate models including CandidateBase, CandidateCreate, CandidateUpdate, Candidate, CandidateOut, CandidateResponse, and CandidateReport with proper validation.
* **Key Technologies/Libraries Used:** Pydantic, EmailStr, UUID, DateTime, Optional types.

#### File: backend/models/interview.py
* **Purpose:** Interview-related Pydantic models and schemas.
* **Content Summary:** Defines comprehensive interview models including enums for interview types, difficulty levels, focus areas, avatar choices, voice choices, and various interview configuration models.
* **Key Technologies/Libraries Used:** Pydantic, Enum, Field Validation, JSON, Complex Types.

#### File: backend/models/response.py
* **Purpose:** Standardized API response models.
* **Content Summary:** Implements generic StandardResponse model with success/error handling and helper functions for creating standardized API responses.
* **Key Technologies/Libraries Used:** Pydantic, Generic Types, Response Standardization.

---

### Folder: backend/utils/
**Purpose:** Utility functions and helper modules.

#### File: backend/utils/__init__.py
* **Purpose:** Utils package initialization.
* **Content Summary:** Empty package initialization file with package description comment.
* **Key Technologies/Libraries Used:** Python package system.

#### File: backend/utils/auth.py
* **Purpose:** Authentication and authorization utilities.
* **Content Summary:** Implements JWT token creation/validation, password hashing, user authentication, role-based access control, and dependency injection for protected routes.
* **Key Technologies/Libraries Used:** JWT, Passlib, Bcrypt, FastAPI Dependencies, HTTP Bearer.

---

### Folder: backend/alembic/
**Purpose:** Database migration management using Alembic.

#### File: backend/alembic.ini
* **Purpose:** Alembic configuration file.
* **Content Summary:** Configuration file for database migration tool with database URL, script location, and migration settings.
* **Key Technologies/Libraries Used:** Alembic, Database Migrations.

#### File: backend/alembic/env.py
* **Purpose:** Alembic environment configuration.
* **Content Summary:** Sets up Alembic environment with database connection, model imports, and migration context configuration.
* **Key Technologies/Libraries Used:** Alembic, SQLAlchemy, Database Migrations.

#### File: backend/alembic/script.py.mako
* **Purpose:** Alembic migration template.
* **Content Summary:** Template file for generating new migration scripts with proper structure and imports.
* **Key Technologies/Libraries Used:** Alembic, Mako Templates.

---

## Frontend Directory (`frontend/`)

**Purpose:** React-based frontend application providing user interface for the AI interview system.

### File: frontend/package.json
* **Purpose:** Node.js project configuration and dependencies.
* **Content Summary:** Defines project metadata, dependencies including React, TailwindCSS, Axios, React Router, and development tools. Includes build scripts and browser compatibility settings.
* **Key Technologies/Libraries Used:** React, TailwindCSS, Axios, React Router, Lucide React, React Hook Form, React Hot Toast.

### File: frontend/tailwind.config.js
* **Purpose:** TailwindCSS configuration file.
* **Content Summary:** Configures TailwindCSS with custom color palette, font family, animations, and content paths. Includes primary and secondary color schemes and custom keyframe animations.
* **Key Technologies/Libraries Used:** TailwindCSS, Custom Configuration, Color Palettes, Animations.

### File: frontend/postcss.config.js
* **Purpose:** PostCSS configuration for CSS processing.
* **Content Summary:** Configures PostCSS with TailwindCSS and Autoprefixer plugins for CSS processing and vendor prefixing.
* **Key Technologies/Libraries Used:** PostCSS, TailwindCSS, Autoprefixer.

### File: frontend/public/index.html
* **Purpose:** Main HTML template for the React application.
* **Content Summary:** HTML template with meta tags, title, favicon, Google Fonts integration, and root div for React mounting.
* **Key Technologies/Libraries Used:** HTML5, Meta Tags, Google Fonts, React Mounting.

---

### Folder: frontend/src/
**Purpose:** Source code directory containing React components, services, and utilities.

#### File: frontend/src/App.js
* **Purpose:** Main React application component with routing configuration.
* **Content Summary:** Sets up React Router with public and protected routes, role-based access control, error boundary, and loading states. Includes navigation logic and route protection.
* **Key Technologies/Libraries Used:** React, React Router, Error Boundary, Role-based Access Control.

#### File: frontend/src/index.js
* **Purpose:** React application entry point.
* **Content Summary:** Renders the main App component with AuthProvider context and Toaster for notifications. Includes React StrictMode for development.
* **Key Technologies/Libraries Used:** React, React DOM, Context API, React Hot Toast.

#### File: frontend/src/index.css
* **Purpose:** Global CSS styles and TailwindCSS imports.
* **Content Summary:** Imports TailwindCSS, defines custom CSS classes, animations, and AI avatar styles. Includes responsive design utilities and custom component styles.
* **Key Technologies/Libraries Used:** TailwindCSS, Custom CSS, Animations, AI Avatar Styling.

---

### Folder: frontend/src/contexts/
**Purpose:** React context providers for global state management.

#### File: frontend/src/contexts/AuthContext.js
* **Purpose:** Authentication context for user state management.
* **Content Summary:** Provides authentication state, login/logout functions, user data management, and token handling. Includes automatic token refresh and error handling.
* **Key Technologies/Libraries Used:** React Context, useState, useEffect, Local Storage, Token Management.

#### File: frontend/src/contexts/ToastContext.js
* **Purpose:** Toast notification context for user feedback.
* **Content Summary:** Manages toast notifications with different types (success, error, warning, info), automatic dismissal, and toast state management.
* **Key Technologies/Libraries Used:** React Context, useState, useCallback, Toast Management.

---

### Folder: frontend/src/components/
**Purpose:** Reusable React components for the user interface.

#### File: frontend/src/components/Layout.js
* **Purpose:** Main layout component with navigation and sidebar.
* **Content Summary:** Implements responsive sidebar navigation, user information display, role-based menu items, and logout functionality. Includes mobile-responsive design.
* **Key Technologies/Libraries Used:** React, React Router, Lucide Icons, Responsive Design, Role-based UI.

#### File: frontend/src/components/ErrorBoundary.js
* **Purpose:** Error boundary component for error handling.
* **Content Summary:** Catches JavaScript errors in child components, displays user-friendly error messages, and provides retry functionality. Includes development error details.
* **Key Technologies/Libraries Used:** React Error Boundary, Error Handling, User Experience.

#### File: frontend/src/components/LoadingSpinner.js
* **Purpose:** Reusable loading spinner component.
* **Content Summary:** Provides configurable loading spinner with different sizes, text options, and full-screen capability. Includes CSS animations.
* **Key Technologies/Libraries Used:** React, CSS Animations, Configurable Components.

#### File: frontend/src/components/Toast.js
* **Purpose:** Toast notification component.
* **Content Summary:** Displays toast notifications with different types, auto-dismiss functionality, and smooth animations. Includes close button and type-specific styling.
* **Key Technologies/Libraries Used:** React, CSS Animations, Toast Notifications.

---

### Folder: frontend/src/components/ui/
**Purpose:** Reusable UI components following design system principles.

#### File: frontend/src/components/ui/Button.js
* **Purpose:** Customizable button component.
* **Content Summary:** Implements button component with different variants (primary, secondary, danger, success), sizes, loading states, and icon support. Uses TailwindCSS for styling.
* **Key Technologies/Libraries Used:** React, TailwindCSS, clsx, Icon Support, Variants.

#### File: frontend/src/components/ui/Card.js
* **Purpose:** Card container components.
* **Content Summary:** Provides Card, CardHeader, CardBody, and CardFooter components for structured content layout. Uses consistent styling and spacing.
* **Key Technologies/Libraries Used:** React, TailwindCSS, Component Composition.

#### File: frontend/src/components/ui/Input.js
* **Purpose:** Form input component.
* **Content Summary:** Implements input component with validation states, error handling, and consistent styling. Supports different input types and validation feedback.
* **Key Technologies/Libraries Used:** React, TailwindCSS, Form Validation, Input Types.

---

### Folder: frontend/src/pages/
**Purpose:** Page components for different application routes.

#### File: frontend/src/pages/Login.js
* **Purpose:** User login page component.
* **Content Summary:** Implements login form with email/password fields, form validation, loading states, and error handling. Includes password visibility toggle and navigation to registration.
* **Key Technologies/Libraries Used:** React, React Router, Form Handling, Error Handling, React Hot Toast.

#### File: frontend/src/pages/Dashboard.js
* **Purpose:** Main dashboard page component.
* **Content Summary:** Displays system statistics, quick actions, recent activity, and upcoming interviews. Includes responsive grid layout and interactive elements.
* **Key Technologies/Libraries Used:** React, Lucide Icons, Responsive Grid, Statistics Display.

#### File: frontend/src/pages/PublicInterview.js
* **Purpose:** Public interview page for candidates.
* **Content Summary:** Implements complete interview flow including registration, permission requests, interview session, recording, and completion. Includes AI avatar integration and WebRTC functionality.
* **Key Technologies/Libraries Used:** React, WebRTC, MediaRecorder, AI Services, File Upload, Permission Management.

---

### Folder: frontend/src/services/
**Purpose:** API service layer for backend communication.

#### File: frontend/src/services/api.js
* **Purpose:** Axios configuration and API interceptors.
* **Content Summary:** Sets up Axios instance with base URL, request/response interceptors, automatic token refresh, error handling, and FormData support.
* **Key Technologies/Libraries Used:** Axios, JWT, Token Refresh, Error Handling, Interceptors.

#### File: frontend/src/services/authService.js
* **Purpose:** Authentication API service.
* **Content Summary:** Implements authentication API calls including login, registration, current user retrieval, and token refresh. Handles FormData for login requests.
* **Key Technologies/Libraries Used:** Axios, FormData, Authentication API.

#### File: frontend/src/services/interviewService.js
* **Purpose:** Interview management API service.
* **Content Summary:** Provides API calls for interview creation, retrieval, updates, question generation, and interview management operations.
* **Key Technologies/Libraries Used:** Axios, Interview Management, API Services.

#### File: frontend/src/services/publicInterviewService.js
* **Purpose:** Public interview API service for candidates.
* **Content Summary:** Implements public API calls for interview access, candidate registration, session management, and response submission without authentication.
* **Key Technologies/Libraries Used:** Axios, Public API, File Upload, Session Management.

#### File: frontend/src/services/aiService.js
* **Purpose:** AI services API integration.
* **Content Summary:** Provides API calls for AI services including text-to-speech generation, transcription, and other AI-powered features.
* **Key Technologies/Libraries Used:** Axios, AI Services, Audio Processing.

#### File: frontend/src/services/avatarService.js
* **Purpose:** Avatar visualization and interaction service.
* **Content Summary:** Manages AI avatar creation, animations, expressions, and visual interactions for the interview interface.
* **Key Technologies/Libraries Used:** JavaScript, DOM Manipulation, Avatar Animation, Visual Effects.

---

### Folder: frontend/src/utils/
**Purpose:** Utility functions and helper modules.

#### File: frontend/src/utils/errorHandler.js
* **Purpose:** Error handling utilities and safe API call functions.
* **Content Summary:** Provides error handling utilities, safe API call wrappers, validation helpers, and error message extraction functions.
* **Key Technologies/Libraries Used:** JavaScript, Error Handling, API Wrappers, Validation.

---

## Database Directory (`database/`)

**Purpose:** Database-related files and documentation.

#### File: database/README.md
* **Purpose:** Database documentation and setup instructions.
* **Content Summary:** Contains database schema documentation, setup instructions, and database-related information.
* **Key Technologies/Libraries Used:** Markdown, Database Documentation.

---

## Additional Files

### File: AI_INTEGRATION_README.md
* **Purpose:** Documentation for AI service integration.
* **Content Summary:** Contains information about AI service integration, configuration, and usage within the system.
* **Key Technologies/Libraries Used:** Markdown, AI Documentation.

### File: SYSTEM_OVERVIEW.md
* **Purpose:** High-level system architecture overview.
* **Content Summary:** Provides system architecture documentation, component relationships, and technical overview.
* **Key Technologies/Libraries Used:** Markdown, System Documentation.

### File: favicon.ico
* **Purpose:** Website favicon icon.
* **Content Summary:** Icon file for browser tab display and bookmarks.
* **Key Technologies/Libraries Used:** ICO format, Web Icons.

---

## Key Technologies and Libraries Summary

### Backend Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **MySQL**: Relational database management system
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and settings management
- **Whisper**: OpenAI's speech recognition system
- **TTS**: Text-to-speech conversion
- **Transformers**: HuggingFace's transformer models
- **Redis**: In-memory data structure store

### Frontend Technologies
- **React**: JavaScript library for building user interfaces
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Declarative routing for React
- **Axios**: HTTP client for API requests
- **WebRTC**: Real-time communication for video/audio
- **React Hook Form**: Form state management
- **React Hot Toast**: Toast notification library
- **Lucide React**: Icon library

### Development Tools
- **Node.js**: JavaScript runtime environment
- **Python**: Programming language for backend
- **Git**: Version control system
- **Docker**: Containerization platform
- **PostCSS**: CSS post-processor
- **ESLint**: JavaScript linting tool

---

## Architecture Overview

The AI Avatar Interview System follows a modern full-stack architecture:

1. **Frontend**: React-based SPA with WebRTC capabilities
2. **Backend**: FastAPI REST API with async support
3. **Database**: MySQL with SQLAlchemy ORM
4. **AI Services**: Multiple AI providers for transcription and TTS
5. **File Storage**: Local filesystem for media files
6. **Authentication**: JWT-based with role-based access control
7. **Real-time**: WebRTC for video/audio communication

The system is designed for scalability, maintainability, and extensibility with clear separation of concerns and modern development practices.

