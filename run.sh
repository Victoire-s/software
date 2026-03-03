#!/bin/bash
set -e

echo "Starting Application in detached mode..."
docker compose up -d

echo "Application is running!"
echo "Backend checks: http://localhost:8000/health"
echo "Frontend: http://localhost:3000"
