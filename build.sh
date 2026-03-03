#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Building Docker containers..."
docker compose build

echo "Build complete."
