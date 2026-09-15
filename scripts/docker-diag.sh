#!/usr/bin/env bash
set -e

echo "=== Linux Mint & Docker Diagnostic Tool ==="
echo "[1/4] Checking Docker status..."
systemctl is-active --quiet docker && echo "✔ Docker service is running." || echo "❌ Docker is stopped."

echo "[2/4] Checking containers status..."
docker compose ps

echo "[3/4] Testing PostgreSQL health..."
docker compose exec db pg_isready -U postgres && echo "✔ Database is accepting connections." || echo "❌ Database connection failed."

echo "[4/4] Testing API Health endpoint..."
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        SUCCESS=1
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "Waiting for API to start (Attempt $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done

if [ $SUCCESS -eq 1 ]; then
    echo "✔ API is reachable and healthy (HTTP 200)."
else
    echo "❌ API healthcheck failed."
    echo "--- Last 20 logs from web container ---"
    docker compose logs web --tail=20
fi

echo "=== Diagnostic Complete ==="
