#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./scripts/run_act_host.sh [job] [registry_url] [registry_username] [registry_token] [--use-host-docker]
# Examples:
# ./scripts/run_act_host.sh build-and-push-image ghcr.io/my-org myuser MYTOKEN
# ./scripts/run_act_host.sh build-and-push-image ghcr.io/my-org myuser MYTOKEN --use-host-docker

JOB=${1:-build-and-push-image}
REGISTRY_URL=${2:-}
REGISTRY_USERNAME=${3:-}
REGISTRY_TOKEN=${4:-}
USE_HOST_DOCKER=false
if [ "${5-}" = "--use-host-docker" ]; then
  USE_HOST_DOCKER=true
fi

if [ -z "$REGISTRY_URL" ] || [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_TOKEN" ]; then
  echo "Missing registry args. You can also export REGISTRY_URL/REGISTRY_USERNAME/REGISTRY_TOKEN as env vars."
  echo "Usage: $0 [job] [registry_url] [registry_username] [registry_token] [--use-host-docker]"
  exit 2
fi

# If on macOS and not using host network, recommend host.docker.internal
if [ "$USE_HOST_DOCKER" = true ]; then
  echo "Using host networking for containers (requires Docker support)."
  NETWORK_ARG=(--container-network host)
else
  echo "Not using host networking; if your Gitea is on the Docker host and act containers cannot reach localhost:3000, re-run with --use-host-docker or set origin to http://host.docker.internal:3000"
  NETWORK_ARG=()
fi

# Run act with provided secrets
act -j "$JOB" "${NETWORK_ARG[@]}" \
  -s REGISTRY_URL="$REGISTRY_URL" \
  -s REGISTRY_USERNAME="$REGISTRY_USERNAME" \
  -s REGISTRY_TOKEN="$REGISTRY_TOKEN" \
  --verbose
