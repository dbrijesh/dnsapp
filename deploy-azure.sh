#!/bin/bash

# Azure Container Apps Deployment Script for Lead-Up App
# This script deploys the application with:
# - Azure Container Registry for Docker images
# - Azure Blob Storage for course materials
# - SQLite database (embedded in container)
# - Min instances = 0 (no charges when idle)

set -e

# Configuration - UPDATE THESE VALUES
RESOURCE_GROUP="leadup-rg"
LOCATION="eastus"
ACR_NAME="leadupacr"  # Must be globally unique (lowercase, alphanumeric only)
STORAGE_ACCOUNT="leadupstorage"  # Must be globally unique (lowercase, alphanumeric only)
CONTAINER_NAME="course-materials"
ENVIRONMENT_NAME="leadup-env"
APP_NAME="leadup-app"
SECRET_KEY=$(openssl rand -base64 32)

echo "============================================"
echo "Lead-Up App - Azure Container Apps Deployment"
echo "============================================"
echo ""
echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Container Registry: $ACR_NAME"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo "  App Name: $APP_NAME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "Step 1: Logging in to Azure..."
az login

# Create Resource Group
echo ""
echo "Step 2: Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo ""
echo "Step 3: Creating Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Create Storage Account
echo ""
echo "Step 4: Creating Azure Storage Account..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Create Blob Container
echo ""
echo "Step 5: Creating Blob Container for course materials..."
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --auth-mode login

# Get Storage Connection String
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)

echo "Storage Connection String obtained"

# Build and Push Docker Image
echo ""
echo "Step 6: Building and pushing Docker image..."
az acr build \
  --registry $ACR_NAME \
  --image leadup-app:latest \
  --file Dockerfile \
  .

# Create Container Apps Environment
echo ""
echo "Step 7: Creating Container Apps Environment..."
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy Container App with min instances = 0
echo ""
echo "Step 8: Deploying Container App (min instances = 0 for cost savings)..."
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image "$ACR_LOGIN_SERVER/leadup-app:latest" \
  --target-port 8000 \
  --ingress external \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 3 \
  --env-vars \
    SECRET_KEY="$SECRET_KEY" \
    DEBUG=False \
    USE_AZURE_SQL=False \
    USE_AZURE_STORAGE=True \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
    AZURE_STORAGE_CONTAINER_NAME="$CONTAINER_NAME" \
    ALLOWED_HOSTS="*"

# Get the App URL
APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "============================================"
echo "Deployment Complete! 🎉"
echo "============================================"
echo ""
echo "Application URL: https://$APP_URL"
echo ""
echo "Important Notes:"
echo "  ✅ Min instances set to 0 - NO CHARGES when idle"
echo "  ✅ App will auto-start on first request (cold start ~10-15 seconds)"
echo "  ✅ Using SQLite database (data persists in container)"
echo "  ✅ Using Azure Blob Storage for course materials"
echo ""
echo "Next Steps:"
echo "  1. Visit: https://$APP_URL"
echo "  2. Create superuser: az containerapp exec --name $APP_NAME --resource-group $RESOURCE_GROUP --command 'python manage.py createsuperuser'"
echo "  3. Load sample data: az containerapp exec --name $APP_NAME --resource-group $RESOURCE_GROUP --command 'python manage.py create_sample_data'"
echo ""
echo "To view logs:"
echo "  az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "To update the app:"
echo "  1. Make changes to code"
echo "  2. Run: az acr build --registry $ACR_NAME --image leadup-app:latest --file Dockerfile ."
echo "  3. Restart app: az containerapp revision restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
