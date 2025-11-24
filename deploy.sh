#!/bin/bash
# Deploy Blog Cover Generator to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Blog Cover Generator - Cloud Run Deploy${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project configured${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${YELLOW}Project ID:${NC} $PROJECT_ID\n"

# Configuration
SERVICE_NAME="blog-cover-generator"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}Warning: GOOGLE_API_KEY environment variable not set${NC}"
    echo -e "The app will run in MOCK_MODE without it.\n"
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build the container
echo -e "${YELLOW}Step 1/3: Building Docker image...${NC}"
docker build -t $IMAGE_NAME:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}\n"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Push to Container Registry
echo -e "${YELLOW}Step 2/3: Pushing to Google Container Registry...${NC}"
docker push $IMAGE_NAME:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image pushed successfully${NC}\n"
else
    echo -e "${RED}✗ Docker push failed${NC}"
    exit 1
fi

# Deploy to Cloud Run
echo -e "${YELLOW}Step 3/3: Deploying to Cloud Run...${NC}"

DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --port 8080"

# Add environment variables if set
if [ ! -z "$GOOGLE_API_KEY" ]; then
    DEPLOY_CMD="$DEPLOY_CMD --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY"
fi

# Execute deployment
eval $DEPLOY_CMD

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Deployment successful!${NC}\n"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${YELLOW}Service URL:${NC} $SERVICE_URL"
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "1. Visit your app: $SERVICE_URL"
    echo "2. Monitor logs: gcloud run services logs tail $SERVICE_NAME --region $REGION"
    echo "3. Update env vars: gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars KEY=VALUE"
    echo ""
else
    echo -e "\n${RED}✗ Deployment failed${NC}"
    exit 1
fi
