#!/usr/bin/env bash
set -euo pipefail

# Deploys the Infrabot-NLP service to Google Cloud Run.
# - Builds the Docker image
# - Pushes to Artifact Registry
# - Manages the GOOGLE_API_KEY in Secret Manager
# - Deploys to Cloud Run with the necessary environment variables.
#
# Usage:
#   ./deploy.sh [GOOGLE_API_KEY]
# or set env before:
#   export GOOGLE_API_KEY=your_key
#   ./deploy.sh
#
# Optional env overrides:
#   PROJECT_ID (default: awanmasterpiece)
#   REGION     (default: us-central1)
#   SERVICE    (default: infrabot-nlp)
#   REPO       (default: infrabot-nlp)
#   GCLOUD_MCP_SERVER_URL (default: https://gcloud-mcp-361046956504.us-central1.run.app)

# --- Configuration ---
PROJECT_ID=${PROJECT_ID:-awanmasterpiece}
REGION=${REGION:-us-central1}
SERVICE=${SERVICE:-infrabot-nlp}
REPO=${REPO:-infrabot-nlp}
GCLOUD_MCP_SERVER_URL=${GCLOUD_MCP_SERVER_URL:-https://gcloud-mcp-361046956504.us-central1.run.app}
PLATFORM=${PLATFORM:-linux/amd64}
SECRET_NAME="infrabot-google-api-key"

# --- Read API Key ---
# Read key from the first script argument or from an environment variable.
API_KEY_FROM_ARG=${1:-${GOOGLE_API_KEY:-}}

# --- Image Path ---
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"

# --- Script Start ---
echo "[INFO] Project:   ${PROJECT_ID}"
echo "[INFO] Region:    ${REGION}"
echo "[INFO] Service:   ${SERVICE}"
echo "[INFO] Image:     ${IMAGE_PATH}"
echo "[INFO] MCP URL:   ${GCLOUD_MCP_SERVER_URL}"

printf "\n[STEP] Configuring gcloud project\n"
gcloud config set project "${PROJECT_ID}" >/dev/null

echo "[STEP] Enabling required services (idempotent)"
gcloud services enable artifactregistry.googleapis.com run.googleapis.com secretmanager.googleapis.com >/dev/null

echo "[STEP] Ensuring Artifact Registry repo exists"
if ! gcloud artifacts repositories describe "${REPO}" --location="${REGION}" >/dev/null 2>&1; then
  echo "[INFO] Artifact Registry repo '${REPO}' not found. Creating..."
  gcloud artifacts repositories create "${REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Repository for ${SERVICE} images"
fi

echo "[STEP] Configuring Docker auth for Artifact Registry"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q

echo "[STEP] Building image (platform: ${PLATFORM})"
docker build --platform="${PLATFORM}" -t "${IMAGE_PATH}" .

echo "[STEP] Pushing image"
docker push "${IMAGE_PATH}"

echo "[STEP] Preparing Secret Manager: ${SECRET_NAME}"
if ! gcloud secrets describe ${SECRET_NAME} >/dev/null 2>&1; then
  echo "[INFO] Secret '${SECRET_NAME}' not found. Creating..."
  gcloud secrets create ${SECRET_NAME} --replication-policy=automatic
fi

if [[ -n "${API_KEY_FROM_ARG}" ]]; then
  echo "[INFO] Provided GOOGLE_API_KEY. Adding as new secret version."
  printf '%s' "${API_KEY_FROM_ARG}" | gcloud secrets versions add ${SECRET_NAME} --data-file=- >/dev/null
else
  echo "[INFO] No GOOGLE_API_KEY provided. Reusing latest secret version if available."
fi

echo "[STEP] Checking for enabled secret versions"
set +e
ENABLED_SECRET_VERSION=$(gcloud secrets versions list ${SECRET_NAME} \
  --filter='state=ENABLED' \
  --format='value(name)' \
  --limit=1 2>/dev/null)
set -e
if [[ -n "${ENABLED_SECRET_VERSION}" ]]; then
  echo "[INFO] Found enabled secret version: ${ENABLED_SECRET_VERSION}"
  USE_SECRET_FLAG=1
else
  echo "[WARN] No enabled secret versions found for ${SECRET_NAME}. The application may not function correctly."
  USE_SECRET_FLAG=0
fi

echo "[STEP] Determining Cloud Run service account"
SA_EMAIL=$(gcloud run services describe "${SERVICE}" --region="${REGION}" --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || true)
if [[ -z "${SA_EMAIL}" ]]; then
  echo "[INFO] Could not determine existing service account. Using default compute service account."
  PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')
  SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
fi
echo "[INFO] Using service account: ${SA_EMAIL}"

echo "[STEP] Granting Secret Manager access to service account (idempotent)"
gcloud secrets add-iam-policy-binding ${SECRET_NAME} \
  --member=serviceAccount:${SA_EMAIL} \
  --role=roles/secretmanager.secretAccessor >/dev/null

echo "[STEP] Deploying to Cloud Run"
# Build the arguments for the deploy command
DEPLOY_ARGS=(
  "${SERVICE}"
  "--image" "${IMAGE_PATH}"
  "--platform" managed
  "--region" "${REGION}"
  "--allow-unauthenticated"
  "--port=8080"
  "--timeout=300s"
  "--set-env-vars=GCLOUD_MCP_SERVER_URL=${GCLOUD_MCP_SERVER_URL}"
)

# Add secret only if it exists and is enabled
if [[ ${USE_SECRET_FLAG} -eq 1 ]]; then
  DEPLOY_ARGS+=(--set-secrets=GOOGLE_API_KEY=${SECRET_NAME}:latest)
fi

gcloud run deploy "${DEPLOY_ARGS[@]}"

printf "\n[DONE] Deployment complete.\n"
echo "[INFO] Service URL: $(gcloud run services describe ${SERVICE} --region ${REGION} --format='value(status.url)')"
