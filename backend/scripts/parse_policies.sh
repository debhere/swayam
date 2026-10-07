#!/usr/bin/env bash
set -e

# Sync dependencies defined in pyproject.toml / uv.lock
uv sync

# Run scripts using the synced environment
uv run python -m backend.ingestion.parser