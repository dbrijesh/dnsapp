# Lead-Up App - Leadership Training Portal

A comprehensive 12-month leadership training portal with SSO authentication, learner progress tracking, and an admin portal for managing curriculum, assessments, and badges.

## Features

### Learner Portal
- **Dashboard**: Progress metrics, upcoming tasks, and 12-month completion status
- **My Program**: 12-month curriculum structure with locked progression
- **Lessons**: Video, audio, document, and text-based lessons with progress tracking
- **Onboarding**: Pledge acceptance and self-assessment forms
- **Badges**: Gamification system with earned badges
- **Assessments**: Rating scale questionnaires and assessments

### Admin Portal
- **Program Management**: Create and manage leadership programs
- **Curriculum Structure**: Organize content into months → modules → lessons
- **Material Management**: Upload videos, PDFs, audio files to Azure Blob Storage
- **Assessment Builder**: Create questionnaires with rating scales
- **Badge Management**: Define badges with earning criteria
- **Onboarding Templates**: Configure pledge and assessment for each program

### Technical Features
- **SSO Authentication**: Azure AD integration with local fallback
- **Dual Database**: SQLite for local development, Azure SQL for production
- **Azure Blob Storage**: Cloud storage for course materials
- **Docker Support**: Container-ready for Azure Container Apps
- **Professional UI**: Sidebar navigation, progress bars, status indicators

## Quick Start

### Local Development (Without Azure)

1. **Clone the repository**
   ```bash
   cd E:\LeadUpCC
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env file - for local testing, defaults are fine
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   # Follow prompts to create admin account
   ```

7. **Create static files directory**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Application: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - Login with superuser credentials created in step 6

### Setting Up Your First Program

1. **Access Django Admin** (http://localhost:8000/admin)

2. **Create a Program**
   - Go to Admin Portal → Programs → Create Program
   - Title: "Leadership Excellence Program 2024"
   - Description: "A comprehensive 12-month journey to develop your leadership skills"
   - Duration: 12 months

3. **Add Months**
   - Click on the program → Add Month
   - Month 1: "Foundation of Leadership"
   - Add learning objectives and description

4. **Add Modules**
   - Click on Month → Add Module
   - Choose type: Behavioral, Technical, or Domain
   - Add title and description

5. **Add Lessons**
   - Click on Module → Add Lesson
   - Upload content (video, document, audio, or text)
   - Set duration and order

6. **Create Onboarding Template**
   - Go to Program → Create Onboarding
   - Add pledge text and welcome message
   - Create self-assessment questionnaire

7. **Register as a Learner**
   - Go to http://localhost:8000/accounts/register
   - Create learner account
   - Enroll in the program

## Deployment to Azure Container Apps

### Prerequisites
- Azure CLI installed
- Azure subscription
- Docker installed

### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name leadup-rg --location eastus

# Create Azure SQL Database
az sql server create --name leadup-sql-server --resource-group leadup-rg --location eastus --admin-user sqladmin --admin-password YourPassword123!
az sql db create --resource-group leadup-rg --server leadup-sql-server --name leadup-db --service-objective S0

# Create Azure Storage Account
az storage account create --name leadupstorage --resource-group leadup-rg --location eastus --sku Standard_LRS
az storage container create --name course-materials --account-name leadupstorage
```

### 2. Build and Push Docker Image

```bash
# Build Docker image
docker build -t leadup-app .

# Tag for Azure Container Registry (if using ACR)
docker tag leadup-app <your-registry>.azurecr.io/leadup-app:latest

# Push to registry
docker push <your-registry>.azurecr.io/leadup-app:latest
```

### 3. Deploy to Azure Container Apps

```bash
# Create Container Apps environment
az containerapp env create --name leadup-env --resource-group leadup-rg --location eastus

# Deploy container app
az containerapp create \
  --name leadup-app \
  --resource-group leadup-rg \
  --environment leadup-env \
  --image <your-registry>.azurecr.io/leadup-app:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    SECRET_KEY=your-production-secret-key \
    DEBUG=False \
    USE_AZURE_SQL=True \
    AZURE_SQL_SERVER=leadup-sql-server.database.windows.net \
    AZURE_SQL_DATABASE=leadup-db \
    AZURE_SQL_USER=sqladmin \
    AZURE_SQL_PASSWORD=YourPassword123! \
    USE_AZURE_STORAGE=True \
    AZURE_STORAGE_CONNECTION_STRING=<connection-string> \
    ALLOWED_HOSTS=<your-app-url>.azurecontainerapps.io
```

### 4. Configure Azure AD SSO (Optional)

1. Register application in Azure AD
2. Configure redirect URIs
3. Update environment variables:
   ```
   USE_AZURE_AD_SSO=True
   AZURE_AD_CLIENT_ID=<client-id>
   AZURE_AD_CLIENT_SECRET=<client-secret>
   AZURE_AD_TENANT_ID=<tenant-id>
   ```

## Project Structure

```
LeadUpCC/
├── leadup/                 # Main project settings
├── accounts/              # User authentication and profiles
├── programs/              # Program, Month, Module, Lesson models
├── learners/              # Learner portal views and templates
├── admins/                # Admin portal views and templates
├── core/                  # Shared utilities (storage, etc.)
├── templates/             # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── learners/
│   └── admins/
├── static/                # Static files (CSS, JS, images)
│   └── css/
│       └── style.css
├── media/                 # User-uploaded files (local dev)
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Environment Variables

See `.env.example` for all available configuration options.

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (local), Azure SQL (production)
- **Storage**: Local filesystem (dev), Azure Blob Storage (production)
- **Authentication**: Django auth, Azure AD SSO (optional)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Deployment**: Docker, Azure Container Apps
- **Server**: Gunicorn

## Admin Access

After deployment, create a superuser:

```bash
# Local
python manage.py createsuperuser

# Azure Container Apps
az containerapp exec --name leadup-app --resource-group leadup-rg --command "python manage.py createsuperuser"
```

## Support & Documentation

For issues and questions, refer to:
- Django documentation: https://docs.djangoproject.com/
- Azure Container Apps: https://learn.microsoft.com/azure/container-apps/
- Bootstrap: https://getbootstrap.com/

## License

Proprietary - All rights reserved
