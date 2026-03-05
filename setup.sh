#!/bin/bash

if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://astral.sh/uv/install.sh | sh
else
    echo "Error: Neither curl nor wget is installed." >&2
    exit 1
fi
