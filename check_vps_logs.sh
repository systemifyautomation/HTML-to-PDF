#!/bin/bash
# Run this on your VPS to check Docker logs

echo "=== Checking if code was pulled ==="
git log --oneline -1

echo ""
echo "=== Checking Docker containers ==="
docker-compose ps

echo ""
echo "=== Checking recent logs (last 50 lines) ==="
docker-compose logs --tail=50 web

echo ""
echo "=== Checking for temp file related errors ==="
docker-compose logs web | grep -i "temp\|file\|error" | tail -20
