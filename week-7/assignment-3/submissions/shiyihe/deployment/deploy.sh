#!/bin/bash

PROJECT_ID="your-project-id"
SERVICE_NAME="mtcars-api"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

podman build -t ${SERVICE_NAME} .

podman tag ${SERVICE_NAME} ${IMAGE}
podman push ${IMAGE}

gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars MODEL_PATH=/app/model.pkl,LOG_LEVEL=INFO,MAX_BATCH_SIZE=100 \
  --set-secrets API_KEY=api-key:latest
