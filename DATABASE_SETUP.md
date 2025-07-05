# Database Setup for Render Deployment

## 🗄️ Database Options

### Option 1: Use SQLite (Default - No Setup Required)
The application will automatically use SQLite if no PostgreSQL database is configured.

**Pros:**
- ✅ No setup required
- ✅ Works immediately
- ✅ Good for testing and small applications

**Cons:**
- ❌ Not suitable for production with multiple users
- ❌ Data not persistent across deployments
- ❌ Limited concurrent connections

### Option 2: Use PostgreSQL (Recommended for Production)

#### Step 1: Create PostgreSQL Database in Render
1. Go to your Render dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Choose a name (e.g., "student-management-db")
4. Select a plan (Free tier available)
5. Click **"Create Database"**

#### Step 2: Get Database Credentials
After creating the database, you'll see:
- **Database Name**
- **User**
- **Password**
- **Host**
- **Port** (usually 5432)

#### Step 3: Add Environment Variables
In your web service settings, add these environment variables:

```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
```

#### Step 4: Redeploy
The build script will automatically:
1. Detect the database configuration
2. Run migrations
3. Set up the database schema

## 🔧 Environment Variables Summary

### Required for Basic Deployment:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
ENCRYPTION_KEY=your-encryption-key
```

### Optional (for PostgreSQL):
```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
```

### Optional (for Email):
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## 🚀 Quick Start (SQLite)

If you want to deploy quickly without setting up PostgreSQL:

1. **Don't set any database environment variables**
2. **The app will use SQLite automatically**
3. **Deploy and test immediately**

## 🔄 Migration from SQLite to PostgreSQL

If you start with SQLite and want to switch to PostgreSQL later:

1. **Create PostgreSQL database** in Render
2. **Add database environment variables**
3. **Redeploy** - migrations will run automatically
4. **Data will be fresh** (SQLite data won't transfer)

## 🐛 Troubleshooting

### "Connection refused" Error
- ✅ **Fixed**: Build script now skips migrations if no database is configured
- ✅ **Fixed**: Settings fall back to SQLite if database variables are missing

### Database Migration Errors
- Ensure all database environment variables are set
- Check database credentials are correct
- Verify database is accessible from Render

### Performance Issues
- Use PostgreSQL for production with multiple users
- Consider database connection pooling for high traffic
- Monitor database performance in Render dashboard 