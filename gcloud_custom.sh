#!/bin/bash

source .env

gcloud iam service-accounts create "build-${APP_NAME_LOWERCASE}-dev-sa" \
  --description="Service account for build process in ${APP_NAME_LOWERCASE} development environment" \
  --display-name="Build ${APP_NAME_LOWERCASE} Dev SA" \
  --project=$GCLOUD_ID

SA_EMAIL="build-${APP_NAME_LOWERCASE}-dev-sa@${GCLOUD_ID}.iam.gserviceaccount.com"

ROLES=(
  "roles/storage.objectAdmin"
  "roles/artifactregistry.writer"
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/secretmanager.secretAccessor"
  "roles/cloudbuild.builds.editor"
  "roles/logging.admin"
)

for ROLE in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding $GCLOUD_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$ROLE"
done

echo "Custom service account permissions:"
gcloud projects get-iam-policy $GCLOUD_ID \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:$SA_EMAIL"
