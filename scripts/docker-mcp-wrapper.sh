#!/bin/bash
# Docker MCP wrapper — the Docker-control via the MCP-lane (the container-management!)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
export DOCKER_HOST="tcp://72.61.71.211:2376"  # the Clinic-Docker (or unix:///var/run/docker.sock!)
exec npx -y docker-mcp-server
