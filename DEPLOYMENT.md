# Azure Deployment Guide - Lead-Up App

This guide will help you deploy the Lead-Up App to Azure Container Apps with Blob Storage for course materials.

## 🎯 Deployment Configuration

- **Container Registry**: Azure Container Registry (for Docker images)
- **Compute**: Azure Container Apps (serverless containers)
- **Storage**: Azure Blob Storage (for course materials - videos, PDFs, etc.)
- **Database**: SQLite (embedded in container)
- **Min Instances**: 0 (no charges when idle)
- **Max Instances**: 3 (auto-scales based on traffic)

## 💰 Cost Optimization

- **Min instances = 0**: Pay ONLY when app is in use
- **Cold start**: ~10-15 seconds on first request after idle
- **Auto-sleep**: App shuts down automatically when not in use
- **Estimated cost**: $0-5/month for light usage

## 📋 Prerequisites

1. **Azure Account**: [Sign up for free](https://azure.microsoft.com/free/)
2. **Azure CLI**: [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Docker**: Docker is NOT required locally (we use Azure ACR build)

## 🚀 Quick Deployment (Automated)

### Windows (PowerShell):

```powershell
# Navigate to project directory
cd E:\LeadUpCC

# Run deployment script
.\deploy-azure.ps1
```

### Linux/Mac (Bash):

```bash
# Navigate to project directory
cd /path/to/LeadUpCC

# Make script executable
chmod +x deploy-azure.sh

# Run deployment script
./deploy-azure.sh
```

The script will:
1. ✅ Login to Azure
2. ✅ Create Resource Group
3. ✅ Create Azure Container Registry
4. ✅ Create Azure Blob Storage
5. ✅ Build and push Docker image
6. ✅ Deploy to Container Apps (min instances = 0)
7. ✅ Display your app URL

**Deployment time**: ~15-20 minutes

## 📝 Manual Deployment Steps

If you prefer manual deployment or need to customize:

### 1. Login to Azure

```bash
az login
```

### 2. Set Variables

```bash
# Update these values
RESOURCE_GROUP="leadup-rg"
LOCATION="eastus"
ACR_NAME="leadupacr"  # Must be globally unique
STORAGE_ACCOUNT="leadupstorage"  # Must be globally unique
APP_NAME="leadup-app"
```

### 3. Create Resources

```bash
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Create Storage Account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create Blob Container
az storage container create \
  --name course-materials \
  --account-name $STORAGE_ACCOUNT \
  --auth-mode login
```

### 4. Build and Push Image

```bash
# Build using Azure (no local Docker needed!)
az acr build \
  --registry $ACR_NAME \
  --image leadup-app:latest \
  --file Dockerfile \
  .
```

### 5. Deploy Container App

```bash
# Get credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query connectionString -o tsv)

# Create Container Apps Environment
az containerapp env create \
  --name leadup-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy app with min instances = 0
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment leadup-env \
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
    SECRET_KEY="your-secret-key-here" \
    DEBUG=False \
    USE_AZURE_SQL=False \
    USE_AZURE_STORAGE=True \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
    AZURE_STORAGE_CONTAINER_NAME="course-materials" \
    ALLOWED_HOSTS="*"
```

### 6. Get App URL

```bash
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

## 🔧 Post-Deployment Setup

### Create Admin User

```bash
az containerapp exec \
  --name leadup-app \
  --resource-group leadup-rg \
  --command "python manage.py createsuperuser"
```

### Load Sample Data

```bash
az containerapp exec \
  --name leadup-app \
  --resource-group leadup-rg \
  --command "python manage.py create_sample_data"
```

## 📊 Monitoring & Management

### View Logs

```bash
az containerapp logs show \
  --name leadup-app \
  --resource-group leadup-rg \
  --follow
```

### Check App Status

```bash
az containerapp show \
  --name leadup-app \
  --resource-group leadup-rg
```

### Scale Configuration

```bash
# Update min/max replicas
az containerapp update \
  --name leadup-app \
  --resource-group leadup-rg \
  --min-replicas 0 \
  --max-replicas 5
```

## 🔄 Updating the Application

### Method 1: Rebuild and Deploy

```bash
# Rebuild image
az acr build \
  --registry $ACR_NAME \
  --image leadup-app:latest \
  --file Dockerfile \
  .

# Restart app (pulls new image)
az containerapp revision restart \
  --name leadup-app \
  --resource-group leadup-rg
```

### Method 2: Update Specific Settings

```bash
# Update environment variables
az containerapp update \
  --name leadup-app \
  --resource-group leadup-rg \
  --set-env-vars "DEBUG=False"
```

## 🗑️ Cleanup (Delete Everything)

To avoid charges, delete all resources:

```bash
az group delete --name leadup-rg --yes --no-wait
```

## ⚠️ Important Notes

### SQLite Database Persistence

- ⚠️ **Data is NOT persistent** across container restarts
- When container is recreated, the SQLite database is lost
- For production with persistent data, consider:
  - Azure SQL Database
  - PostgreSQL on Azure
  - Mount Azure Files volume

### Current Setup (Development/Testing)

- ✅ Perfect for: Development, testing, demos
- ❌ Not ideal for: Production with important data
- 💡 Solution: Run `create_sample_data` after each deployment

### Cost Considerations

- Container Apps: ~$0 (min instances = 0)
- Storage Account: ~$0.01-0.50/month
- Container Registry: ~$5/month (Basic tier)
- **Total estimated: ~$5-6/month**

## 🔐 Security Best Practices

1. **Change SECRET_KEY**: Use a secure random key
2. **Set DEBUG=False**: Always in production
3. **Configure ALLOWED_HOSTS**: Set to your domain
4. **Enable HTTPS**: Automatic with Container Apps
5. **Use Managed Identity**: For storage access (optional)

## 📞 Support

If deployment fails:

1. Check Azure CLI version: `az --version`
2. Check resource names are unique
3. Check Azure subscription has quota
4. View deployment logs
5. Check [Azure Status](https://status.azure.com/)

## 🎯 Next Steps After Deployment

1. ✅ Visit your app URL
2. ✅ Create admin user
3. ✅ Load sample data
4. ✅ Upload course materials (they go to Blob Storage)
5. ✅ Create custom programs and content
6. ✅ Share the URL with learners!

---

**Ready to deploy?** Run the deployment script and your app will be live in ~15-20 minutes! 🚀
