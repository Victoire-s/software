#!/bin/bash
set -e

echo "Ensure docker is running for tests..."
docker compose up -d backend mysql

echo "Running tests inside the backend container..."
# Using docker compose exec so it runs against the mapped folder if needed, or docker compose run
docker compose exec -T backend pytest -v

echo "Tests finished."
