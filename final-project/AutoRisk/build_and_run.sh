#!/usr/bin/env bash
# AutoRisk — build and run with Podman
# Usage: bash build_and_run.sh [push]
set -euo pipefail

PROJECT_ID="${GCP_PROJECT:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"
PUSH=${1:-""}

echo "=== Building AutoRisk API image ==="
podman build -f api/Dockerfile -t autorisk-api:latest .

echo "=== Building AutoRisk App image ==="
podman build -f app/Dockerfile -t autorisk-app:latest .

if [ "$PUSH" = "push" ]; then
  echo "=== Tagging for Google Container Registry ==="
  podman tag autorisk-api:latest gcr.io/${PROJECT_ID}/autorisk-api:latest
  podman tag autorisk-app:latest gcr.io/${PROJECT_ID}/autorisk-app:latest

  echo "=== Pushing images ==="
  podman push gcr.io/${PROJECT_ID}/autorisk-api:latest
  podman push gcr.io/${PROJECT_ID}/autorisk-app:latest

  echo "=== Deploying API to Cloud Run ==="
  gcloud run deploy autorisk-api \
    --image gcr.io/${PROJECT_ID}/autorisk-api:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1

  API_URL=$(gcloud run services describe autorisk-api \
    --region ${REGION} --format "value(status.url)")

  echo "=== Deploying App to Cloud Run (API_URL=${API_URL}) ==="
  gcloud run deploy autorisk-app \
    --image gcr.io/${PROJECT_ID}/autorisk-app:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars API_URL=${API_URL}

  APP_URL=$(gcloud run services describe autorisk-app \
    --region ${REGION} --format "value(status.url)")
  echo ""
  echo "✅ Deployed!"
  echo "   API: ${API_URL}"
  echo "   App: ${APP_URL}"
else
  echo ""
  echo "=== Running locally with podman-compose ==="
  podman-compose up --build
fi
