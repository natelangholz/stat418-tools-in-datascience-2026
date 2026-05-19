#!/bin/bash
# Build the API image with Podman, push to GCR, and deploy to Cloud Run.
#
# Usage: PROJECT_ID=your-project ./deployment/deploy.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID, e.g. PROJECT_ID=my-project ./deployment/deploy.sh}"
SERVICE="market-value-api"
REGION="${REGION:-us-central1}"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE}"

echo "==> Building image with Podman"
podman build -t "${SERVICE}" .

echo "==> Tagging and pushing to GCR"
podman tag "${SERVICE}" "${IMAGE}"
podman push "${IMAGE}"

echo "==> Deploying to Cloud Run"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars MODEL_PATH=/app/model.pkl,LOG_LEVEL=INFO,MAX_BATCH_SIZE=100 \
  --set-secrets API_KEY=market-value-api-key:latest

echo "==> Done. Service URL:"
gcloud run services describe "${SERVICE}" --region "${REGION}" --format 'value(status.url)'
