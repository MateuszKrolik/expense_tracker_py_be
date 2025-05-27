#! /bin/zsh

source .env

SA_EMAIL="build-${APP_NAME_LOWERCASE}-dev-sa@${GCLOUD_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts keys create gcp-credentials.json \
  --iam-account=$SA_EMAIL
