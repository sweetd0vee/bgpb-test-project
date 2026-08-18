#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-bgpb-ml}"

docker compose -f "$ROOT/docker-compose.yml" up -d --build
