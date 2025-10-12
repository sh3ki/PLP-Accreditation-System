# PLP Accreditation System - Setup Guide

This guide will help you set up the PLP Accreditation System on a new computer.

## Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)
- Firebase project with Firestore enabled
- Cloudinary account (for image uploads)

## Step-by-Step Setup Instructions

### 1. Navigate to Project Directory

```powershell
cd "C:\path\to\your\PLP Accreditation System"
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
```

### 3. Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**If you get an execution policy error in PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Upgrade pip (Optional but Recommended)

```powershell
python -m pip install --upgrade pip
```

### 5. Install Dependencies

Navigate to the `accreditation` folder and install requirements:

```powershell
cd accreditation
pip install -r requirements.txt
```

### 6. Configure Firebase

#### 6.1 Get Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `accreditation-6af94`
3. Click on the gear icon (⚙️) → Project settings
4. Go to the "Service accounts" tab
5. Click "Generate new private key"
6. Save the downloaded JSON file as `firebase-service-account.json`

#### 6.2 Place the File

Copy the `firebase-service-account.json` file to the `accreditation` directory:
```
PLP Accreditation System/
└── accreditation/
    ├── firebase-service-account.json  ← Place it here
    ├── manage.py
    └── ...
```

⚠️ **Important:** Never commit this file to Git! It's already in `.gitignore`.

### 7. Configure Cloudinary (Optional)

If you're using image upload features:

1. Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` file with your Cloudinary credentials:
```
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Get your credentials from: https://cloudinary.com/console

### 8. Database Setup

The project uses:
- **Firebase Firestore** - Primary database for application data
- **SQLite** - Local database for Django sessions and internal operations

#### 8.1 Initialize Django Database

```powershell
python manage.py migrate
```

#### 8.2 Initialize Firebase Collections and Data

Run the initialization commands:

```powershell
# Initialize departments and roles in Firebase
python manage.py init_departments_roles

# Create default users (optional - for testing)
python manage.py create_default_users
```

### 9. Verify Firebase Connection

Test if Firebase is properly connected:

```powershell
python manage.py test_firebase
```

You should see: "Firebase initialized successfully!"

### 10. Run the Development Server

```powershell
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

### 11. Access the Application

1. Open your browser and go to: http://127.0.0.1:8000/login/
2. Use the default credentials (if you ran `create_default_users`):
   - **Admin:** `admin@plp.ac.ke` / password from the command output
   - **QA Head:** `qahead@plp.ac.ke` / password from the command output
   - **Department Head:** `depthead@plp.ac.ke` / password from the command output

## Common Issues and Solutions

### Issue 1: PowerShell Script Execution Disabled

**Error:** "cannot be loaded because running scripts is disabled on this system"

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Firebase Not Initialized

**Error:** "Warning: Firebase service account file not found!"

**Solution:**
- Make sure `firebase-service-account.json` exists in the `accreditation` folder
- Verify the file is valid JSON and downloaded from your Firebase project

### Issue 3: Module Not Found Errors

**Error:** "ModuleNotFoundError: No module named 'firebase_admin'"

**Solution:**
```powershell
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### Issue 4: Port Already in Use

**Error:** "Error: That port is already in use."

**Solution:**
```powershell
# Run on a different port
python manage.py runserver 8001
```

Or find and kill the process using port 8000:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

## Project Structure

```
PLP Accreditation System/
└── accreditation/
    ├── manage.py                          # Django management script
    ├── requirements.txt                   # Python dependencies
    ├── db.sqlite3                         # SQLite database (auto-created)
    ├── firebase-service-account.json      # Firebase credentials (DO NOT COMMIT)
    ├── .env                               # Environment variables (DO NOT COMMIT)
    ├── accreditation/                     # Main Django app
    │   ├── settings.py                    # Django settings
    │   ├── urls.py                        # URL routing
    │   ├── firebase_auth.py               # Firebase authentication
    │   ├── firebase_utils.py              # Firebase utilities
    │   └── ...
    ├── firebase_app/                      # Firebase app module
    │   ├── management/commands/           # Custom management commands
    │   └── ...
    └── templates/                         # HTML templates
        ├── dashboard/
        ├── auth/
        └── components/
```

## Additional Management Commands

### User Management

```powershell
# Verify password status of users
python manage.py verify_password_status

# Update password change flags
python manage.py update_users_password_changed

# Clean up old password fields
python manage.py cleanup_password_fields

# Add profile pictures (if needed)
python manage.py add_profile_pictures
```

### Department Management

```powershell
# Update department active status
python update_departments_active.py

# Update CCS department logo
python update_ccs_logo.py
```

## Development Workflow

1. **Start coding session:**
   ```powershell
   cd accreditation
   .\venv\Scripts\Activate.ps1
   python manage.py runserver
   ```

2. **Make changes** to your code

3. **If you modify models or add migrations:**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Stop server:** Press `Ctrl+C` in the terminal

## Deployment Considerations

Before deploying to production:

1. **Change DEBUG to False** in `settings.py`
2. **Generate a new SECRET_KEY**
3. **Configure ALLOWED_HOSTS**
4. **Use environment variables** for sensitive data
5. **Set up proper database** (PostgreSQL recommended)
6. **Configure static files** for production
7. **Set up HTTPS**
8. **Configure proper logging**

## Support

For issues or questions:
- Check the documentation files in the project root
- Review the implementation summaries (e.g., `IMPLEMENTATION_SUMMARY.md`)
- Check Firebase console for database issues

## Important Security Notes

⚠️ **NEVER commit these files to version control:**
- `firebase-service-account.json`
- `.env`
- `db.sqlite3` (contains session data)

These are already included in `.gitignore`, but double-check before pushing to any repository.

---

**Last Updated:** October 12, 2025
