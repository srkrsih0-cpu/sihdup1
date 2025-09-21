# OmniAttend - AI-Powered Institutional Management & Student Success Platform

## 🎓 Next-Gen Educational Platform with Modern UI/UX

OmniAttend is a comprehensive, AI-powered educational management platform designed for institutions of all sizes. With enterprise-grade security, real-time processing, and a beautiful modern interface, it transforms how educational institutions manage attendance and student success.

## 🌟 Key Features

### 🔐 Enterprise-Grade Security
- Advanced authentication with JWT
- Rate limiting (5 login attempts/minute)
- Input validation for all forms
- CSRF protection
- Security headers with Talisman
- Password strength validation

### 📁 Advanced Data Management
- CSV/Excel bulk upload for students, teachers, and timetables
- Real-time validation and error handling
- Batch operations for efficient processing
- File security with 16MB limit and type validation

### 🎨 Modern UI/UX Design
- Zomato/Swiggy-inspired gradients and smooth animations
- Animated transitions with Flutter Animate
- Loading placeholders with Shimmer
- Custom animated cards and components
- Responsive design for all screen sizes

### ⚡ Real-time Processing
- Instant data validation and error handling
- Face recognition attendance with DeepFace
- Real-time attendance analytics
- Dynamic AI-powered student routines

### 🛡️ Zero-Error Experience
- Comprehensive error handling and user feedback
- Loading states for all operations
- Offline support for core features
- Auto-retry for failed network requests

## 🏗️ Architecture & Tech Stack

### Backend (Python Flask)
- **Core**: Flask, SQLAlchemy, Flask-Migrate
- **AI & Recognition**: DeepFace, TensorFlow, Google Generative AI
- **Security**: Flask-Limiter, Flask-Talisman, Bcrypt, JWT
- **File Processing**: Pandas, OpenPyXL, XLRD
- **Utilities**: Werkzeug, Pillow

### Frontend (Flutter Mobile App)
- **UI Framework**: Flutter with Material Design
- **Animations**: Animated Text Kit, Flutter Animate
- **Loading States**: Shimmer, Flutter SpinKit
- **State Management**: Provider
- **File Handling**: File Picker
- **Networking**: HTTP, Shared Preferences

## 🚀 Quick Setup & Deployment

### Prerequisites
- Python 3.13+
- Flutter 3.24+
- Git for version control

### Backend Setup
```bash
cd sih/sih_smart_app/sih_smart_app/backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export GEMINI_API_KEY="your-google-gemini-api-key"
export SECRET_KEY="your-secure-secret-key"

# Initialize database
python init_college_data.py

# Start server
python app.py
```

### Frontend Setup
```bash
cd sih/sih_smart_app/sih_smart_app/frontend/mobile_app

# Install dependencies
flutter pub get

# Run app
flutter run
```

## 🎯 User Roles & Features

### Institution Admin
- **Complete CRUD Operations**: Manage institutions, branches, semesters, subjects
- **User Management**: Add/remove students and teachers
- **Bulk Operations**: CSV/Excel import for students and teachers
- **Schedule Management**: Create and manage class timetables
- **Analytics Dashboard**: Institutional-level attendance reports

### Teacher
- **Photo-Based Attendance**: Single photo captures entire classroom
- **AI Recognition**: Automatic student identification
- **Manual Review**: Override attendance before finalizing
- **Attendance Analytics**: View class and student attendance statistics
- **Schedule Management**: Access daily class schedules

### Student
- **Real-time Attendance Tracking**: View current attendance percentages
- **AI-Powered Routines**: Personalized daily schedules
- **Smart Suggestions**: Academic tasks based on interests and goals
- **Attendance Warnings**: Proactive alerts for low attendance
- **Career Guidance**: Tasks aligned with long-term goals

## 📊 API Endpoints

### Authentication
- `POST /api/login` - User login with rate limiting
- `POST /api/register_institution` - Institution registration

### Admin Operations
- `GET/POST/PUT/DELETE /api/admin/institutions` - Institution management
- `GET/POST/PUT/DELETE /api/admin/branches` - Branch management
- `GET/POST/PUT/DELETE /api/admin/semesters` - Semester management
- `GET/POST/PUT/DELETE /api/admin/subjects` - Subject management
- `GET/POST/PUT/DELETE /api/admin/schedules` - Class schedule management
- `POST /api/admin/upload/students` - Bulk student import
- `POST /api/admin/upload/teachers` - Bulk teacher import
- `POST /api/admin/upload/timetable` - Bulk timetable import

### Teacher Operations
- `GET /api/teacher/:id/timetable/today` - Today's schedule
- `GET /api/class/:id/roster` - Class roster
- `GET /api/class/:id/attendance` - Attendance records
- `POST /api/mark_attendance` - Face recognition
- `POST /api/save_attendance` - Save attendance

### Student Operations
- `POST /api/student/:id/profile` - Update profile
- `GET /api/student/:id/smart_routine` - AI-powered routine
- `GET /api/student/:id/attendance/stats` - Attendance statistics
- `GET /api/student/:id/attendance/history` - Attendance history

## 🎉 Sample Data Formats

### Students CSV
```csv
college_id,name,email,phone,branch_code,semester_number,password
21B81A0506,John Doe,john@college.edu,9876543210,CSE,3,student123
```

### Teachers CSV
```csv
college_id,name,email,phone,department,designation,password
TEA_012,Dr. New Faculty,faculty@college.edu,9876543212,CSE,Professor,teacher123
```

### Timetable CSV
```csv
subject_code,teacher_college_id,room,day_of_week,start_time,end_time
CS301,TEA_001,Room-101,0,09:00,10:00
```

## 🔧 Development

### Backend Development
```bash
# Run tests
python -m pytest tests/

# Run with hot reload
python app.py
```

### Frontend Development
```bash
# Run with hot reload
flutter run

# Run tests
flutter test

# Analyze code
flutter analyze
```

## 🚀 Production Deployment

### Environment Configuration
```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export GEMINI_API_KEY="your-gemini-api-key"
export FLASK_ENV="production"
```

### Server Deployment
```bash
# Install production server
pip install gunicorn redis

# Run with security features
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📈 Performance Monitoring

- Backend request timing logs
- Frontend page load time tracking
- Database query optimization
- Memory usage monitoring

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Generative AI for powering the smart suggestions
- DeepFace for facial recognition capabilities
- Flutter community for the amazing UI framework