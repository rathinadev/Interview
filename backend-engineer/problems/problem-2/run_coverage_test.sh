#!/bin/bash

echo "🚀 Starting E2E test for microservices..."

# 1. Clean up
docker compose down -v

# 2. Build and start services
docker compose up --build -d

# 3. Wait for Postgres to be healthy
echo "⏳ Waiting for PostgreSQL to be healthy..."
until [ "$(docker inspect -f {{.State.Health.Status}} "$(docker compose ps -q postgres)")" == "healthy" ]; do
    sleep 1;
done
echo "✅ PostgreSQL is healthy."

# 4. Create databases
echo "🗂️ Creating databases..."
docker compose exec postgres createdb -U interview_user user_db || true
docker compose exec postgres createdb -U interview_user product_db || true
docker compose exec postgres createdb -U interview_user order_db || true
echo "✅ Databases created."

# 5. Run table creation via temporary containers
echo "🏗️ Creating tables..."
docker compose run --rm user_service python -c "from app import database; database.init_db()"
docker compose run --rm product_service python -c "from app import database; database.init_db()"
docker compose run --rm order_service python -c "from app import database; database.init_db()"
echo "✅ Tables created."

# 6. Wait for services to be fully up and running
sleep 5

# 7. Run the test
echo "🧪 Running end-to-end tests..."
pytest tests/
TEST_EXIT_CODE=$?

# 8. Clean up
echo "🛑 Shutting down services..."
docker compose down -v

exit $TEST_EXIT_CODE