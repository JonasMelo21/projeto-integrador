#!/bin/bash
# Deploy script for Azure Container Apps
# Usage: ./deploy.sh [build|push|deploy|all]

set -e

# Configuration
REGISTRY_NAME="rentmasteracr"
REGISTRY_URL="${REGISTRY_NAME}.azurecr.io"
IMAGE_NAME="populate-db"
IMAGE_TAG="latest"
RESOURCE_GROUP="rg_rent_master_dev"
CONTAINER_APP_NAME="populate-db"
CONTAINER_APP_ENV="env_rent_master"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}
    log_info "✅ Image built: ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}"
}

# Push to Azure Container Registry
push_image() {
    log_info "Pushing image to ACR..."
    az acr build \
        --registry ${REGISTRY_NAME} \
        --image ${IMAGE_NAME}:${IMAGE_TAG} \
        --file Dockerfile \
        .
    log_info "✅ Image pushed to ACR"
}

# Deploy or update Container App
deploy_app() {
    log_info "Deploying Container App..."
    
    # Check if Container App exists
    if az containerapp show \
        --name ${CONTAINER_APP_NAME} \
        --resource-group ${RESOURCE_GROUP} &>/dev/null; then
        
        log_info "Updating existing Container App..."
        az containerapp update \
            --name ${CONTAINER_APP_NAME} \
            --resource-group ${RESOURCE_GROUP} \
            --image ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}
    else
        log_info "Creating new Container App..."
        az containerapp create \
            --name ${CONTAINER_APP_NAME} \
            --resource-group ${RESOURCE_GROUP} \
            --environment ${CONTAINER_APP_ENV} \
            --image ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG} \
            --cpu 0.5 \
            --memory 1Gi \
            --trigger-type schedule \
            --cron-expression "0 1 * * *" \
            --environment-variables \
                STORAGE_ACCOUNT_NAME=rentmasterstorageaccount \
                CONTAINER_NAME=bronze \
                DB_PATH=/data/rental.db \
                LOG_LEVEL=INFO \
            --secrets \
                email-password=${EMAIL_PASSWORD} \
                email-to=${EMAIL_TO} \
            --environment-variables \
                EMAIL_FROM=python_pipeline@gmail.com \
                EMAIL_PASSWORD=secretref:email-password \
                EMAIL_TO=secretref:email-to \
            --registry-server ${REGISTRY_URL} \
            --registry-username $(az acr credential show --name ${REGISTRY_NAME} --query username -o tsv) \
            --registry-password $(az acr credential show --name ${REGISTRY_NAME} --query passwords[0].value -o tsv)
    fi
    
    log_info "✅ Container App deployed/updated"
}

# Show usage
usage() {
    echo "Usage: $0 [build|push|deploy|all]"
    echo ""
    echo "Commands:"
    echo "  build   - Build Docker image locally"
    echo "  push    - Push to Azure Container Registry"
    echo "  deploy  - Deploy/update Container App"
    echo "  all     - Build, push, and deploy"
    echo ""
    echo "Environment variables:"
    echo "  EMAIL_PASSWORD - Gmail App Password (required for deploy)"
    echo "  EMAIL_TO       - Recipient email (required for deploy)"
}

# Main
case "${1:-all}" in
    build)
        build_image
        ;;
    push)
        push_image
        ;;
    deploy)
        deploy_app
        ;;
    all)
        build_image
        push_image
        deploy_app
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac

log_info "✅ Done!"
