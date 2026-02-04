# Azure Container Apps Deployment Script for Lead-Up App (PowerShell)
# This script deploys the application with:
# - Azure Container Registry for Docker images
# - Azure Blob Storage for course materials
# - SQLite database (embedded in container)
# - Min instances = 0 (no charges when idle)

# Configuration - UPDATE THESE VALUES
$RESOURCE_GROUP = "leadup-rg"
$LOCATION = "eastus"
$ACR_NAME = "leadupacr"  # Must be globally unique (lowercase, alphanumeric only)
$STORAGE_ACCOUNT = "leadupstorage"  # Must be globally unique (lowercase, alphanumeric only)
$CONTAINER_NAME = "course-materials"
$ENVIRONMENT_NAME = "leadup-env"
$APP_NAME = "leadup-app"
$SECRET_KEY = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Lead-Up App - Azure Container Apps Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:"
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  Location: $LOCATION"
Write-Host "  Container Registry: $ACR_NAME"
Write-Host "  Storage Account: $STORAGE_ACCOUNT"
Write-Host "  App Name: $APP_NAME"
Write-Host ""

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Azure CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Login to Azure
Write-Host "Step 1: Logging in to Azure..." -ForegroundColor Yellow
az login

# Create Resource Group
Write-Host ""
Write-Host "Step 2: Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
Write-Host ""
Write-Host "Step 3: Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $ACR_NAME `
  --sku Basic `
  --admin-enabled true

# Get ACR credentials
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv

Write-Host "ACR Login Server: $ACR_LOGIN_SERVER" -ForegroundColor Green

# Create Storage Account
Write-Host ""
Write-Host "Step 4: Creating Azure Storage Account..." -ForegroundColor Yellow
az storage account create `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2

# Create Blob Container
Write-Host ""
Write-Host "Step 5: Creating Blob Container for course materials..." -ForegroundColor Yellow
az storage container create `
  --name $CONTAINER_NAME `
  --account-name $STORAGE_ACCOUNT `
  --auth-mode login

# Get Storage Connection String
$STORAGE_CONNECTION_STRING = az storage account show-connection-string `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --query connectionString -o tsv

Write-Host "Storage Connection String obtained" -ForegroundColor Green

# Build and Push Docker Image
Write-Host ""
Write-Host "Step 6: Building and pushing Docker image..." -ForegroundColor Yellow
az acr build `
  --registry $ACR_NAME `
  --image leadup-app:latest `
  --file Dockerfile `
  .

# Create Container Apps Environment
Write-Host ""
Write-Host "Step 7: Creating Container Apps Environment..." -ForegroundColor Yellow
az containerapp env create `
  --name $ENVIRONMENT_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION

# Deploy Container App with min instances = 0
Write-Host ""
Write-Host "Step 8: Deploying Container App (min instances = 0 for cost savings)..." -ForegroundColor Yellow
az containerapp create `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT_NAME `
  --image "$ACR_LOGIN_SERVER/leadup-app:latest" `
  --target-port 8000 `
  --ingress external `
  --registry-server $ACR_LOGIN_SERVER `
  --registry-username $ACR_USERNAME `
  --registry-password $ACR_PASSWORD `
  --cpu 0.5 `
  --memory 1.0Gi `
  --min-replicas 0 `
  --max-replicas 3 `
  --env-vars `
    "SECRET_KEY=$SECRET_KEY" `
    "DEBUG=False" `
    "USE_AZURE_SQL=False" `
    "USE_AZURE_STORAGE=True" `
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" `
    "AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME" `
    "ALLOWED_HOSTS=*"

# Get the App URL
$APP_URL = az containerapp show `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn -o tsv

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deployment Complete! 🎉" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application URL: https://$APP_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Important Notes:"
Write-Host "  ✅ Min instances set to 0 - NO CHARGES when idle" -ForegroundColor Green
Write-Host "  ✅ App will auto-start on first request (cold start ~10-15 seconds)" -ForegroundColor Green
Write-Host "  ✅ Using SQLite database (data persists in container)" -ForegroundColor Green
Write-Host "  ✅ Using Azure Blob Storage for course materials" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Visit: https://$APP_URL"
Write-Host "  2. Create superuser: az containerapp exec --name $APP_NAME --resource-group $RESOURCE_GROUP --command 'python manage.py createsuperuser'"
Write-Host "  3. Load sample data: az containerapp exec --name $APP_NAME --resource-group $RESOURCE_GROUP --command 'python manage.py create_sample_data'"
Write-Host ""
Write-Host "To view logs:"
Write-Host "  az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
Write-Host ""
Write-Host "To update the app:"
Write-Host "  1. Make changes to code"
Write-Host "  2. Run: az acr build --registry $ACR_NAME --image leadup-app:latest --file Dockerfile ."
Write-Host "  3. Restart app: az containerapp revision restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
Write-Host ""
