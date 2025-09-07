import pytest
import json
import time
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fakeredis.aioredis import FakeRedis

from app.main import app
from app.core.db import get_async_db, get_sync_db, get_redis_client
from app.models import Base, Product, Sale

# This ensures the database persists between connections in the same test session,
# avoiding the "no such table" error with ephemeral in-memory databases.
TEST_DB_FILE = "./test.db"
SYNC_SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
ASYNC_SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

# --- Test Engine Setup  ---
sync_engine = create_engine(
    SYNC_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)
TestAsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# --- Dependency Overrides---
fake_redis_client = FakeRedis(decode_responses=True)
async def override_get_redis_client():
    yield fake_redis_client

def override_get_sync_db():
    db = TestSyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def override_get_async_db():
    async with TestAsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_sync_db] = override_get_sync_db
app.dependency_overrides[get_async_db] = override_get_async_db
app.dependency_overrides[get_redis_client] = override_get_redis_client

# --- Pytest Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def setup_test_dbs():
    """
    Creates the database file and tables ONCE for the entire test session.
    Cleans up by deleting the file after all tests are done.
    """
    # Teardown any previous file
    if os.path.exists(TEST_DB_FILE):
        os.unlink(TEST_DB_FILE)
        
    # Setup: Create tables for both engines on the same file
    Base.metadata.create_all(bind=sync_engine)
    
    yield  # Run all the tests
    
    # Teardown: Delete the database file
    os.unlink(TEST_DB_FILE)


@pytest.fixture(scope="function", autouse=True)
async def manage_data_between_tests():
    """
    Manages DATA between tests, not the schema.
    It cleans all tables after each test to ensure test isolation.
    """
    yield # Run the test

    # Teardown: Clean all data from tables
    await fake_redis_client.flushall()
    with TestSyncSessionLocal() as db:
        db.execute(delete(Sale))
        db.execute(delete(Product))
        db.commit()


# This fixture is now just for inserting data for each test.
@pytest.fixture(scope="function", autouse=True)
def populate_data(manage_data_between_tests):
    """Populates the database with fresh data before each test."""
    with TestSyncSessionLocal() as db:
        test_data = [
            Product(id=1, name="Laptop", category="electronics"),
            Product(id=2, name="Mouse", category="electronics"),
            Product(id=3, name="Book", category="books"),
            Sale(product_id=1, quantity=10), Sale(product_id=1, quantity=5),
            Sale(product_id=2, quantity=20), Sale(product_id=3, quantity=50)
        ]
        db.add_all(test_data)
        db.commit()


@pytest.fixture(scope="function")
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# --- Test Cases ---
@pytest.mark.asyncio
async def test_read_slow_report(async_client: AsyncClient):
    response = await async_client.get("/report/slow?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "database"
    report = data["report"]
    assert report[0] == {"name": "Mouse", "total_quantity": 20}

@pytest.mark.asyncio
async def test_read_fast_report_cache_miss(async_client: AsyncClient):
    response = await async_client.get("/report/fast?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "database"
    report = data["report"]
    assert report[0] == {"name": "Mouse", "total_quantity": 20}
    cached_data = await fake_redis_client.get("report:electronics")
    assert cached_data is not None

@pytest.mark.asyncio
async def test_read_fast_report_cache_hit(async_client: AsyncClient):
    await async_client.get("/report/fast?category=electronics")
    response = await async_client.get("/report/fast?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "cache"
    report = data["report"]
    assert report[0]["name"] == "Mouse"
@pytest.mark.asyncio
async def test_performance_difference(async_client: AsyncClient):
    """
    Demonstrates the performance difference and prints explicit comparisons.
    """
    # --- 1. Time the slow, synchronous endpoint ---
    start_time_slow = time.perf_counter()
    await async_client.get("/report/slow?category=electronics")
    duration_slow = time.perf_counter() - start_time_slow
    print(f"\n/report/slow (sync DB) took:      {duration_slow:.6f} seconds")

    # --- 2. Time the fast endpoint (cache miss) ---
    start_time_fast_miss = time.perf_counter()
    await async_client.get("/report/fast?category=electronics")
    duration_fast_miss = time.perf_counter() - start_time_fast_miss
    print(f"/report/fast (async DB) took:     {duration_fast_miss:.6f} seconds")

    # --- 3. Time the fast endpoint (cache hit) ---
    start_time_fast_hit = time.perf_counter()
    await async_client.get("/report/fast?category=electronics")
    duration_fast_hit = time.perf_counter() - start_time_fast_hit
    print(f"/report/fast (from cache) took:   {duration_fast_hit:.6f} seconds")

    # --- Assertions ---
    assert duration_fast_hit < duration_slow
    assert duration_fast_hit < duration_fast_miss
    print("\n--> Test confirms that the cache hit is the fastest.")

    print("\n--- Performance Comparison ---")
    # Add small checks to prevent division by zero if a duration is incredibly small
    if duration_fast_miss > 0:
        print(f"The async DB query was {duration_slow / duration_fast_miss:.2f}x faster than the sync DB query.")
    
    if duration_fast_hit > 0:
        print(f"The cache hit was {duration_slow / duration_fast_hit:.2f}x faster than the sync DB query.")
        print(f"The cache hit was {duration_fast_miss / duration_fast_hit:.2f}x faster than the async DB query.")
