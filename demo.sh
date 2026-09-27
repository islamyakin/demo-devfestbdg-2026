set -euo pipefail
URL=$(gcloud run services describe code-runner-$1 --region asia-southeast1 --format='value(status.url)')
AUTH="Authorization: Bearer $(gcloud auth print-identity-token)"
if [ "$2" = state ]; then
  curl -s -H "$AUTH" "$URL/state"
else
  curl -s -H "$AUTH" -X POST --data-binary @"$2" "$URL/execute"
fi
