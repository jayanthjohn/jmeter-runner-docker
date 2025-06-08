#!/bin/bash
set -e

if [[ -n "$GITHUB_URL" && -n "$GITHUB_TOKEN" && -n "$RUNNER_NAME" ]]; then
  echo "📦 Registering GitHub Runner..."
  cd /actions-runner

  if [ ! -f .runner ]; then
    ./config.sh --url "$GITHUB_URL" \
                --token "$GITHUB_TOKEN" \
                --name "$RUNNER_NAME" \
                --work _work \
                --unattended \
                --replace
  fi

  echo "🚀 Starting GitHub Runner..."
  exec ./run.sh
else
  echo "🔧 No GitHub runner config found. Starting container in interactive mode..."
  exec /bin/bash
fi