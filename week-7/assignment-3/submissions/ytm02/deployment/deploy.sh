#!/bin/bash
# deploy.sh — Build, push, and deploy the Iris API to Google Cloud Run
set -euo pipefail

# ── Configuration (edit these) ────────────────────────────────────────────────
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="iris-classifier-api"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=== Building image with Podman ==="
podman build -t "${SERVICE_NAME}" .

echo "=== Testing locally ==="
podman run --rm -d \
  -p 8080:8080 \
  -e PORT=8080 \
  -e API_KEY=test123 \
  -e MODEL_PATH=/app/model.pkl \
  --name "${SERVICE_NAME}-test" \
  "${SERVICE_NAME}"

sleep 3
curl -sf http://localhost:8080/health && echo " Health OK"
podman stop "${SERVICE_NAME}-test"

echo "=== Tagging and pushing to GCR ==="
podman tag "${SERVICE_NAME}" "${IMAGE}"
podman push "${IMAGE}"

echo "=== Deploying to Cloud Run ==="
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars MODEL_PATH=/app/model.pkl,LOG_LEVEL=INFO,MAX_BATCH_SIZE=100 \
  --set-secrets API_KEY=iris-api-key:latest \
  --project "${PROJECT_ID}"

echo "=== Deployment complete ==="
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format "value(status.url)")
echo "Service URL: ${SERVICE_URL}"
echo "Health check: curl ${SERVICE_URL}/health"
