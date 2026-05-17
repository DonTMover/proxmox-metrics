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
# Optional fifth argument may be GITEA_TOKEN or the --no-host-network flag.
GITEA_TOKEN_ENV=${GITEA_TOKEN:-}
GITEA_TOKEN=""

# Default to using host network so containers can reach host services (Gitea on localhost)
USE_HOST_DOCKER=true
if [ "${5-}" = "--no-host-network" ]; then
  USE_HOST_DOCKER=false
elif [ -n "${5-}" ]; then
  # treat 5th arg as GITEA_TOKEN unless it's the network flag
  GITEA_TOKEN="${5}"
  if [ "${6-}" = "--no-host-network" ]; then
    USE_HOST_DOCKER=false
  fi
fi
# prefer environment variable if set
if [ -n "$GITEA_TOKEN_ENV" ]; then
  GITEA_TOKEN="$GITEA_TOKEN_ENV"
fi

# Require registry args only for image-publish jobs
case "$JOB" in
  *push*|*build-and-push*|*publish*)
    if [ -z "$REGISTRY_URL" ] || [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_TOKEN" ]; then
      echo "Missing registry args for job $JOB. Provide REGISTRY_URL/REGISTRY_USERNAME/REGISTRY_TOKEN."
      echo "Usage: $0 [job] [registry_url] [registry_username] [registry_token] [--no-host-network]"
      exit 2
    fi
    ;;
  *)
    # no registry required
    ;;
esac

# If on macOS and not using host network, recommend host.docker.internal
if [ "$USE_HOST_DOCKER" = true ]; then
  echo "Using host networking for containers (requires Docker support)."
  NETWORK_ARG=(--container-network host)
else
  echo "Not using host networking; if your Gitea is on the Docker host and act containers cannot reach localhost:3000, re-run with --use-host-docker or set origin to http://host.docker.internal:3000"
  NETWORK_ARG=()
fi

# Run act with provided secrets
ACT_CMD=(act -j "$JOB" "${NETWORK_ARG[@]}")
ACT_CMD+=( -s REGISTRY_URL="$REGISTRY_URL" )
ACT_CMD+=( -s REGISTRY_USERNAME="$REGISTRY_USERNAME" )
ACT_CMD+=( -s REGISTRY_TOKEN="$REGISTRY_TOKEN" )
# pass Gitea token to act if provided (keeps token out of repo)
if [ -n "$GITEA_TOKEN" ]; then
  ACT_CMD+=( -s GITEA_TOKEN="$GITEA_TOKEN" )
fi
ACT_CMD+=( --verbose )

"${ACT_CMD[@]}"
