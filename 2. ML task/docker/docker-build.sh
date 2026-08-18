#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-bgpb-ml}"
TAG="${TAG:-latest}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker build -t "${IMAGE}:${TAG}" .
