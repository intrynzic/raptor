#!/usr/bin/env bash

set -e

# Detect if script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script must be sourced, not executed."
    echo "Run: source scripts/dev.sh"
    return 1 2>/dev/null || exit 1
fi

export UV_CACHE_DIR="$PWD/.uv_cache"

uv venv --clear
uv sync
source .venv/bin/activate
