# Quick Start Guide - Lead-Up App

This guide will help you get the Lead-Up App running in minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation Steps

### 1. Create Virtual Environment

```bash
cd E:\LeadUpCC
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
copy .env.example .env
```

For local development, the default values in `.env.example` work perfectly. No changes needed!

### 5. Initialize Database

```bash
python manage.py migrate
```

### 6. Create Sample Data

```bash
python manage.py create_sample_data
```

This creates:
- A complete sample program with months, modules, and lessons
- Demo learner account: `learner@example.com` / `password123`
- Demo admin account: `admin@example.com` / `admin123`
- Sample badges and assessments

### 7. Create Static Files Directory

```bash
python manage.py collectstatic --noinput
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

### 9. Access the Application

Open your browser and navigate to:

- **Main App**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **Learner Portal**: http://localhost:8000/learners/dashboard/
- **Admin Portal**: http://localhost:8000/admins/

## Demo Accounts

### Learner Account
- **Email**: learner@example.com
- **Password**: password123
- **Features**: Access to dashboard, program, lessons, badges

### Admin Account
- **Email**: admin@example.com
- **Password**: admin123
- **Features**: Full admin access + learner features

## Next Steps

### As a Learner:
1. Login with learner credentials
2. Complete onboarding (pledge + assessment)
3. Start exploring the program curriculum
4. Complete lessons and track your progress

### As an Admin:
1. Login with admin credentials
2. Go to Admin Portal
3. Create additional programs, months, modules, and lessons
4. Upload course materials (videos, PDFs, documents)
5. Create badges and assessments

## Common Tasks

### Create Your Own Program

1. Login as admin
2. Go to Admin Portal → Programs → Create Program
3. Add months to your program
4. Add modules to each month
5. Add lessons to each module
6. Create onboarding template for the program

### Add Course Materials

When creating/editing lessons:
- **Videos**: Upload MP4 files
- **Documents**: Upload PDF files
- **Audio**: Upload MP3 files
- **Text**: Enter content directly in the text editor

### Enroll New Learners

1. Users register at http://localhost:8000/accounts/register/
2. They automatically become learners
3. They can enroll in available programs
4. Complete onboarding to access content

## Troubleshooting

### Issue: Port 8000 already in use

```bash
# Use a different port
python manage.py runserver 8080
```

### Issue: Database errors

```bash
# Delete database and recreate
del db.sqlite3
python manage.py migrate
python manage.py create_sample_data
```

### Issue: Static files not loading

```bash
python manage.py collectstatic --noinput --clear
```

## Development Tips

- The app uses SQLite for local development (no database setup needed!)
- All uploaded files are stored locally in the `media/` folder
- Changes to Python code auto-reload the server
- Changes to templates require manual browser refresh

## Getting Help

Check these resources:
- Full README: `README.md`
- Django documentation: https://docs.djangoproject.com/
- Bootstrap documentation: https://getbootstrap.com/

## Production Deployment

For deploying to Azure Container Apps, see the **Deployment** section in `README.md`.

---

Happy coding! 🚀
