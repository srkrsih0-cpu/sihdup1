# WARP.md - OmniAttend: AI-Powered Institutional Management Platform

## 🚀 **MAJOR UPDATE: Modern UI/UX & Enterprise Security Features**

This file provides comprehensive guidance for developers working with the **enhanced** OmniAttend codebase.

## 🎯 Project Overview

This repository contains a **next-generation OmniAttend Platform** with **modern UI/UX design** and **enterprise-grade security**, developed for educational institutions:

### 🌟 **Latest Enhancements**

1. **🔐 Enterprise Security**: Rate limiting, input validation, CSRF protection, security headers
2. **📁 Advanced File Processing**: CSV/Excel bulk upload for students, teachers, timetables
3. **🎨 Modern UI/UX**: Zomato/Swiggy-inspired gradients, animations, smooth transitions
4. **⚡ Zero-Error Experience**: Comprehensive error handling and user feedback
5. **🛡️ Production Ready**: Enhanced authentication, data validation, and security

### 🏗️ **Core Architecture**

1. **Backend**: Enhanced Flask API with security layers and file processing
2. **Frontend**: Beautiful Flutter app with modern animations and components
3. **Real Data**: Integrated with actual institution data
4. **Project Demo Ready**: Professional interface for presentations

## 🛠️ Enhanced Development Environment Setup

### Backend (Flask) - Enhanced Security

#### Install Enhanced Dependencies

```bash
cd sih/sih_smart_app/sih_smart_app/backend

# Core Flask dependencies
pip install flask flask-sqlalchemy flask-migrate flask-cors

# AI and Recognition
pip install deepface tensorflow PyJWT google-generativeai

# NEW: Enhanced Security & File Processing
pip install flask-limiter openpyxl xlrd flask-wtf
pip install validators passlib email-validator 
pip install flask-login flask-talisman cryptography bcrypt

# Utilities
pip install werkzeug pillow pandas
```

#### Initialize with Real Institution Data

```bash
# IMPORTANT: Populates database with actual institution data
python init_college_data.py

# Start enhanced server with security features
python app.py
```

**🎉 Server starts on**: `http://127.0.0.1:5000` with enhanced security!

### Frontend (Flutter) - Modern UI/UX

#### Install Enhanced UI Dependencies

```bash
cd sih/sih_smart_app/sih_smart_app/frontend/mobile_app

# Install all dependencies including new UI libraries
flutter pub get

# Run the beautiful new app
flutter run
```

**🎨 New UI/UX Libraries Added**:
- ✨ `animated_text_kit` - TypeWriter animations
- 🎨 `flutter_animate` - Smooth transitions  
- ⚡ `shimmer` - Loading placeholders
- 🎆 `flutter_spinkit` - Loading indicators
- 📏 `provider` - State management
- 📁 `file_picker` - CSV/Excel uploads
- 🔗 `connectivity_plus` - Network status

## 🔧 Enhanced Development Tasks

### 🔐 Backend Security Development

#### Test Enhanced Authentication (Rate Limited)

```bash
# Login with rate limiting (5 attempts per minute)
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"college_id": "ADMIN_CSE_001", "password": "admin123"}'

# Test input validation
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"college_id": "invalid", "password": "weak"}'  # Will fail validation
```

#### Test File Upload Endpoints

```bash
# Upload students CSV (with authentication)
curl -X POST http://localhost:5000/api/admin/upload/students \
  -H "Authorization: Bearer <jwt-token>" \
  -F "file=@students.csv"

# Upload teachers Excel
curl -X POST http://localhost:5000/api/admin/upload/teachers \
  -H "Authorization: Bearer <jwt-token>" \
  -F "file=@teachers.xlsx"

# Upload timetable data
curl -X POST http://localhost:5000/api/admin/upload/timetable \
  -H "Authorization: Bearer <jwt-token>" \
  -F "file=@timetable.csv"
```

### 📁 Sample Data Files

#### Students Upload Format (`students.csv`)
```csv
college_id,name,email,phone,branch_code,semester_number,password
21B81A0506,John Doe,john@college.edu,9876543210,CSE,3,student123
21B81A0507,Jane Smith,jane@college.edu,9876543211,CSE,3,student123
```

#### Teachers Upload Format (`teachers.csv`)
```csv
college_id,name,email,phone,department,designation,password
TEA_012,Dr. New Faculty,faculty@college.edu,9876543212,CSE,Professor,teacher123
```

#### Timetable Upload Format (`timetable.csv`)
```csv
subject_code,teacher_college_id,room,day_of_week,start_time,end_time
CS301,TEA_001,Room-101,0,09:00,10:00
CS302,TEA_002,Room-102,1,10:00,11:00
```

### 🎨 Frontend UI/UX Development

#### Run with Hot Reload for UI Development
```bash
cd sih/sih_smart_app/sih_smart_app/frontend/mobile_app

# Start with hot reload to see UI changes instantly
flutter run --hot

# Analyze code quality (should show minimal errors now)
flutter analyze

# Format code consistently
dart format .
```

#### Test UI Components
```bash
# Run specific widget tests
flutter test test/ui_components_test.dart

# Run all tests
flutter test

# Build for release testing
flutter build apk --release
```

## 🔒 Enhanced Security Features

### 🛡️ Security Layers Implemented

#### 1. Rate Limiting
- **Login Protection**: Maximum 5 attempts per minute
- **File Upload Limits**: 10 uploads per hour
- **General API**: 100 requests per hour per IP

#### 2. Input Validation
- **Email Validation**: RFC-compliant email format checking
- **Phone Validation**: International phone number formats
- **College ID**: Alphanumeric with length constraints
- **Password Strength**: 8+ chars, uppercase, numbers, special characters

#### 3. File Security
- **Type Validation**: Only CSV/Excel files allowed
- **Size Limits**: Maximum 16MB per file
- **Content Scanning**: Header validation and structure checking
- **Sanitization**: Filename sanitization and path traversal prevention

#### 4. API Security
- **CSRF Protection**: Form token validation
- **Security Headers**: XSS, injection, and clickjacking protection
- **CORS**: Configured for specific origins only
- **JWT Enhancement**: Secure token generation and validation

### 🔍 Security Testing Commands

```bash
# Test rate limiting
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/login \
    -H "Content-Type: application/json" \
    -d '{"college_id": "test", "password": "wrong"}' \
    --write-out "Attempt $i: %{http_code}\n" --silent --output /dev/null
done

# Test input validation
curl -X POST http://localhost:5000/api/admin/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"college_id": "a", "name": "", "password": "weak", "role": "invalid"}'
```

## 🎨 UI/UX Development Guide

### 🌈 Theme System

The app uses a comprehensive theme system located in `lib/theme/app_theme.dart`:

```dart
// Colors with gradients
AppColors.primaryGradient  // Red to orange gradient
AppColors.secondaryGradient  // Blue to teal gradient
AppColors.successGradient  // Green gradient

// Animations
AppAnimation.fast    // 200ms
AppAnimation.normal  // 300ms
AppAnimation.slow    // 500ms

// Spacing
AppSpacing.xs   // 4px
AppSpacing.sm   // 8px
AppSpacing.md   // 16px
```

### 🧩 Reusable Components

Custom components in `lib/components/ui_components.dart`:

```dart
// Animated login screen
AnimatedTextHeader(text: "OmniAttend")

// Gradient buttons
GradientButton(text: "Login", onPressed: () {})

// Loading states
CustomLoadingIndicator()
ShimmerCard()

// Status badges
StatusBadge.success("Uploaded")
StatusBadge.error("Failed")
```

### 🎭 Animation Examples

```dart
// Smooth page transitions
Navigator.push(context, _createRoute(NewScreen()))

// TypeWriter effect (login screen)
AnimatedTextKit.typeWriter("OmniAttend")

// Card animations
AnimatedCard(onTap: () {}, child: Content())
```

## 📊 Enhanced API Endpoints

### 🆕 New File Upload Endpoints

| Endpoint | Method | Description | Security |
|----------|--------|-------------|----------|
| `/api/admin/upload/students` | POST | Bulk student import | JWT + Rate Limited |
| `/api/admin/upload/teachers` | POST | Bulk teacher import | JWT + Rate Limited |
| `/api/admin/upload/timetable` | POST | Bulk schedule import | JWT + Rate Limited |

### 🔐 Enhanced Authentication

| Endpoint | Method | Rate Limit | Validation |
|----------|--------|------------|------------|
| `/api/login` | POST | 5/minute | Input + Password strength |
| `/api/register_institution` | POST | 3/minute | Email + Phone + Name |

## 🧪 Testing & Quality Assurance

### Backend Testing
```bash
cd sih/sih_smart_app/sih_smart_app/backend

# Test API endpoints
python -m pytest tests/

# Test security features
python test_security.py

# Load testing
python -m locust -f tests/load_test.py
```

### Frontend Testing
```bash
cd sih/sih_smart_app/sih_smart_app/frontend/mobile_app

# Widget tests
flutter test test/widget_test.dart

# UI component tests
flutter test test/ui_components_test.dart

# Integration tests
flutter test integration_test/
```

## 🚀 Production Deployment

### Environment Configuration
```bash
# Production environment variables
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export GEMINI_API_KEY="your-gemini-api-key"
export FLASK_ENV="production"
export RATE_LIMIT_STORAGE_URL="redis://localhost:6379"
```

### Production Server with Enhanced Security
```bash
# Install production server
pip install gunicorn redis

# Run with security features
gunicorn -w 4 -b 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 2 \
  --max-requests 1000 \
  app:app
```

### SSL and HTTPS (Production)
```bash
# With SSL certificate
gunicorn -w 4 -b 0.0.0.0:8000 \
  --certfile=cert.pem \
  --keyfile=key.pem \
  --ssl-version=TLSv1_2 \
  app:app
```

## 🔍 Troubleshooting Enhanced Features

### Common Issues

#### 1. Rate Limiting Issues
```bash
# Check Redis connection (if using Redis for rate limiting)
redis-cli ping

# Reset rate limits (development only)
curl -X DELETE http://localhost:5000/api/admin/reset-limits \
  -H "Authorization: Bearer <admin-token>"
```

#### 2. File Upload Issues
```bash
# Check file permissions
ls -la uploads/

# Test file format
file students.csv  # Should show: ASCII text

# Check file size
du -h students.csv  # Should be < 16MB
```

#### 3. UI/UX Issues
```bash
# Clear Flutter cache
flutter clean
flutter pub get

# Check for conflicts
flutter doctor
flutter analyze
```

## 📈 Performance Monitoring

### Backend Performance
```python
# Monitor request times
from flask import request
import time

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    if duration > 1.0:  # Log slow requests
        app.logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
    return response
```

### Frontend Performance
```dart
import 'package:flutter/services.dart';

class PerformanceMonitor {
  static void trackPageLoad(String pageName) {
    final stopwatch = Stopwatch()..start();

    print('$pageName loaded in ${stopwatch.elapsedMilliseconds}ms');
  }
}
```

## 🎉 **You're Ready to Build Amazing Educational Software!**

The enhanced OmniAttend Platform now provides:

- 🔐 **Bank-level security** with rate limiting and validation
- 📁 **Efficient data management** with CSV/Excel processing  
- 🎨 **Beautiful modern UI** that users will love
- ⚡ **Zero-error experience** with comprehensive feedback
- 🚀 **Production-ready** scalable architecture

**Happy coding! 🎓💻**