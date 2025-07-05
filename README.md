# 🎓 Django Student Management System

A comprehensive web-based student management system built with Django, featuring role-based access control, secure authentication, and robust security features.

## 🌟 Features

### 🔐 Security Features
- **Role-Based Access Control** (Student, Teacher, Admin)
- **Strong Password Validation** (12+ characters, common password detection)
- **CSRF Protection** on all forms
- **Rate Limiting** (5 login attempts/minute, 3 registrations/minute)
- **XSS Protection** with input sanitization
- **File Upload Security** (type validation, size limits)
- **Data Encryption** for sensitive information
- **Security Headers** (HSTS, X-Frame-Options, etc.)

### 👥 User Management
- Student registration and profile management
- Teacher registration and course assignment
- Admin dashboard for system oversight
- Secure authentication and session management

### 📚 Course Management
- Course creation and management
- Enrollment system with approval workflow
- Prerequisite checking
- Course capacity management

### 📊 Dashboard Features
- Role-specific dashboards
- Student schedule viewing
- Teacher course management
- Admin enrollment approval system

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- PostgreSQL (optional, SQLite for development)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/student-management-system.git
cd student-management-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in the project root:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (optional - will use SQLite if not provided)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Encryption
ENCRYPTION_KEY=your-encryption-key-here
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

### 8. Access the Application
Open your browser and go to: `http://127.0.0.1:8000`

## 🏗️ Project Structure

```
Student_management_system/
├── MainApp/                    # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── forms.py               # Form definitions
│   ├── urls.py                # URL routing
│   └── utils/
│       └── encryption.py      # Encryption utilities
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   └── dashboard/             # Dashboard templates
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User uploaded files
├── Student_management_system/  # Django project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
├── requirements.txt            # Python dependencies
├── Procfile                   # Deployment configuration
├── build.sh                   # Build script for deployment
└── manage.py                  # Django management script
```

## 🔧 Configuration

### Development Settings
- `DEBUG=True` - Enables debug mode
- SQLite database (default)
- Relaxed security settings for development

### Production Settings
- `DEBUG=False` - Disables debug mode
- PostgreSQL database recommended
- Strict security headers enabled
- HTTPS enforcement
- Rate limiting active

## 👤 User Roles

### Student
- Register and create profile
- Browse available courses
- Request course enrollment
- View personal schedule
- Update profile information

### Teacher
- Register and create profile
- Manage assigned courses
- Approve/deny enrollment requests
- View enrolled students
- Update course information

### Admin
- Oversee all system operations
- Approve/deny enrollment requests
- Manage user accounts
- System-wide course management
- View system statistics

## 🔒 Security Features Explained

### Authentication & Authorization
- **Custom User Model**: Extends Django's AbstractUser with role-based access
- **Strong Password Policy**: 12+ characters, common password detection
- **Session Security**: Secure session handling with automatic timeout

### Input Validation
- **XSS Protection**: All user inputs sanitized with Bleach library
- **File Upload Security**: Type validation, size limits (5MB max)
- **CSRF Protection**: Tokens on all forms, secure cookie settings

### Rate Limiting
- **Login Protection**: 5 attempts per minute per IP
- **Registration Protection**: 3 attempts per minute per IP
- **Security Logging**: All rate limit violations logged

### Data Protection
- **Encryption**: Sensitive data (addresses) encrypted before storage
- **Secure Headers**: HSTS, X-Frame-Options, Content-Type protection
- **HTTPS Enforcement**: Automatic redirect in production

## 🚀 Deployment

### Render Deployment
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set Build Command: `./build.sh`
4. Set Start Command: `gunicorn Student_management_system.wsgi:application`
5. Add environment variables (see DEPLOYMENT_CHECKLIST.md)

### Environment Variables for Production
```env
SECRET_KEY=your-secure-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DB_NAME=your_production_db_name
DB_USER=your_production_db_user
DB_PASSWORD=your_production_db_password
DB_HOST=your_production_db_host
DB_PORT=5432
ENCRYPTION_KEY=your-secure-production-encryption-key
```

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'app'**
   - ✅ Fixed: Procfile updated with correct WSGI path

2. **DisallowedHost Error**
   - ✅ Fixed: ALLOWED_HOSTS includes localhost and 127.0.0.1

3. **Database Connection Issues**
   - ✅ Fixed: Fallback to SQLite for development

4. **Static Files Not Loading**
   - ✅ Fixed: WhiteNoise middleware configured

### Local Development Commands
```bash
# Navigate to project
cd Student_management_system

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

## 📊 Monitoring & Logs

### Log Files
- Rate limit violations: `logs/ratelimit.log`
- Django application logs
- Deployment logs (Render dashboard)

### Health Checks
- Application responds to root URL
- Database migrations completed
- Static files served correctly
- Security headers present

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
1. Check the troubleshooting section
2. Review the deployment checklist
3. Check Render logs for deployment issues
4. Ensure all environment variables are set correctly

## 🔄 Updates

### Recent Updates
- ✅ Fixed deployment issues
- ✅ Added comprehensive security features
- ✅ Created deployment automation
- ✅ Added rate limiting and logging
- ✅ Enhanced input validation and sanitization

---

**Built with ❤️ using Django and modern security practices** 