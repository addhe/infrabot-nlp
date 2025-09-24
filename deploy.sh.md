#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Deploy Helper for Infrabot NLP on Google Cloud Run
#
# This script automates the deployment process by:
# 1. Configuring the gcloud project and enabling necessary APIs.
# 2. Verifying that the required secret (containing .env content) exists.
# 3. Using Cloud Build to build and deploy the container from source.
# 4. Fetching logs and the service URL upon completion.
#
# Usage:
#   ./deploy.sh
#
# Optional environment variable overrides:
#   PROJECT_ID (default: awanmasterpiece)
#   REGION     (default: asia-southeast2)
#   SERVICE    (default: infrabot-nlp)
#   SECRET_NAME(default: infrabot-env)
# ==============================================================================

# --- Configuration ---
# Set default values for your project configuration.
# These can be overridden by setting environment variables before running the script.
PROJECT_ID=${PROJECT_ID:-awanmasterpiece}
REGION=${REGION:-asia-southeast2}
SERVICE=${SERVICE:-infrabot-nlp}
SECRET_NAME=${SECRET_NAME:-infrabot-env}
SECRET_VERSION=${SECRET_VERSION:-latest}

# --- Print Current Configuration ---
echo "[INFO] Using the following configuration:"
echo "  Project:  ${PROJECT_ID}"
echo "  Region:   ${REGION}"
echo "  Service:  ${SERVICE}"
echo "  Secret:   ${SECRET_NAME}:${SECRET_VERSION}"
echo "--------------------------------------------------"

# --- Pre-flight Checks & Setup ---
echo "[STEP 1/4] Configuring gcloud and enabling services..."

gcloud config set project "${PROJECT_ID}" >/dev/null

# Enable necessary APIs for the deployment. This is idempotent.
gcloud services enable \
  run.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com >/dev/null

echo "[INFO] Required services are enabled."

# --- Secret Verification ---
echo "[STEP 2/4] Verifying that the required secret exists..."

if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "[ERROR] Secret '${SECRET_NAME}' not found in project '${PROJECT_ID}'."
  echo "        Please create it first by following the setup instructions in README.md."
  echo "        The secret's value should be the entire content of your .env file."
  exit 1
fi

echo "[INFO] Secret '${SECRET_NAME}' found."

# --- Deployment ---
echo "[STEP 3/4] Deploying to Cloud Run from source. This may take a few minutes..."

# The --source . flag tells gcloud to use the current directory, build a container
# using Cloud Build, push it to Artifact Registry, and deploy it to Cloud Run.
gcloud run deploy "${SERVICE}" \
  --source . \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars-from-secret="${SECRET_NAME}:${SECRET_VERSION}" \
  --timeout=300s \
  --port=8080 || {
    echo "[ERROR] Deployment failed. Please check the build logs in the Google Cloud Console."
    exit 1
  }

# --- Post-deployment Info ---
echo "[STEP 4/4] Fetching service URL and recent logs..."

SERVICE_URL=$(gcloud run services describe "${SERVICE}" --region "${REGION}" --project="${PROJECT_ID}" --format="value(status.url)")

echo "--------------------------------------------------"
echo "[SUCCESS] Deployment complete!"
echo "[INFO] Service URL: ${SERVICE_URL}"
echo "--------------------------------------------------"

echo "[INFO] Displaying the last 50 log entries:"
gcloud run services logs read "${SERVICE}" --region "${REGION}" --project="${PROJECT_ID}" --limit=50 || echo "[WARN] Could not retrieve logs. The service might still be initializing."
