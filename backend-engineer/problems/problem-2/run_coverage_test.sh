#!/bin/bash

echo "🚀 Starting distributed coverage test for microservices..."

# 1. Clean up
echo "🧹 Cleaning up old containers and coverage data..."
docker compose down -v --remove-orphans
rm -rf ./coverage_data
mkdir -p ./coverage_data

# 2. Build and start services
echo "🏗️ Building and starting services..."
docker compose up --build -d

# 3. Wait for Postgres and create databases
echo "⏳ Waiting for PostgreSQL container to be healthy..."
until [ "$(docker inspect -f {{.State.Health.Status}} "$(docker compose ps -q postgres)")" == "healthy" ]; do
    sleep 1;
done
echo "✅ PostgreSQL is healthy."

echo "🗂️ Creating databases..."
docker compose exec postgres createdb -U interview_user user_db || true
docker compose exec postgres createdb -U interview_user product_db || true
docker compose exec postgres createdb -U interview_user order_db || true
echo "✅ Databases created."

# 4. Wait for application services
echo "⏳ Waiting for application services to initialize..."
sleep 20 

# 5. Run the E2E test
echo "🧪 Running end-to-end tests..."
pytest tests/

# 6. CRITICAL FIX: Get container IDs BEFORE stopping them
echo "🔎 Getting container IDs..."
USER_SERVICE_ID=$(docker compose ps -q user_service)
PRODUCT_SERVICE_ID=$(docker compose ps -q product_service)
ORDER_SERVICE_ID=$(docker compose ps -q order_service)
API_GATEWAY_ID=$(docker compose ps -q api_gateway)

# 7. Stop services gracefully
echo "🛑 Stopping services gracefully..."
docker compose stop

# 8. Copy coverage data from the stopped (but not removed) containers
echo "📊 Copying coverage data from containers..."
docker cp "$USER_SERVICE_ID":/code/.coverage.* ./coverage_data/
docker cp "$PRODUCT_SERVICE_ID":/code/.coverage.* ./coverage_data/
docker cp "$ORDER_SERVICE_ID":/code/.coverage.* ./coverage_data/
docker cp "$API_GATEWAY_ID":/code/.coverage.* ./coverage_data/

# 9. Clean up containers now
echo "🧹 Removing stopped containers..."
docker compose down

# 10. Combine coverage reports
echo "📊 Combining coverage reports..."
coverage combine ./coverage_data/

# 11. Generate and print the final report
echo "✅ Final Combined Coverage Report:"
coverage report -m

# 12. Final cleanup
echo "🧹 Final cleanup..."
rm -rf ./coverage_data