# Solution: Problem 2 - Resilient & Scalable Microservice Architecture

## 1. Executive Summary

This project is a comprehensive and production-minded implementation of a microservice architecture for a distributed e-commerce system. It moves beyond a simple collection of APIs to a cohesive, resilient, and scalable system that embodies modern cloud-native design principles. The solution demonstrates a deep understanding of service decomposition, inter-service communication patterns (both synchronous and asynchronous), fault tolerance, and automated system orchestration with Docker Compose. Every component and interaction has been architected to address the unique challenges of a distributed environment.

## 2. Architectural Deep Dive & Design Rationale

The system is decomposed into four primary microservices, each with a single, well-defined responsibility, fronted by an API Gateway. This decomposition is the foundation for achieving independent scalability, deployment, and fault isolation.

### System Components & Interaction Flow

```
+--------------------------------+       +---------------------------------+      +--------------------------------+
|                                |       |                                 |      |                                |
|        USER SERVICE            |       |           API GATEWAY           |      |       PRODUCT SERVICE          |
|--------------------------------|       |---------------------------------|      |--------------------------------|
| - Owns 'user_db' (PostgreSQL)  |       | - Public Entry Point (Port 8000)|      | - Owns 'product_db' (PostgreSQL)|
| - Manages user lifecycle       |------>| - Routes requests to services   |<---->| - Manages catalog & inventory  |
| - Sole issuer of JWTs          |       | - Validates all incoming JWTs   |      | - Asynchronous Event Consumer  |
|                                |       |                                 |      |                                |
+--------------------------------+       +---------------------------------+      +-----------------+--------------+
                                                     |                                          ^
                                                     |  (Synchronous, blocking HTTP Call)       |  (Asynchronous, non-blocking Event)
                                                     |                                          |
                                                     v                                          |
+--------------------------------+       +---------------------------------+      +------------+-------------------+
|                                |       |                                 |      |                                |
|         ORDER SERVICE          |------>|           RABBITMQ              |----->| (Background Listener Thread in |
|--------------------------------|       |---------------------------------|      |         Product Service)       |
| - Owns 'order_db' (PostgreSQL) |       | - Durable Message Broker        |      |                                |
| - Orchestrates order creation  |       | - Decouples Order & Product     |      |                                |
| - Publishes 'OrderCreated'     |       |   inventory updates             |      |                                |
+--------------------------------+       +---------------------------------+      +--------------------------------+
```

### End-to-End Order Flow: A Step-by-Step Technical Narrative

1.  **Authentication**: A client first interacts with the `/register` and `/token` endpoints. The **API Gateway** proxies these requests directly to the **User Service**. The User Service validates credentials against its private `user_db` and, upon success, signs and issues a short-lived JWT using a shared secret key.

2.  **Authorization**: For all subsequent protected requests, the client includes the JWT in the `Authorization: Bearer` header. The **API Gateway** intercepts every request, validates the JWT's signature and expiration, and extracts the `user_id` from the token's `sub` claim. **Crucially, this is a stateless, cryptographic operation that does not require a network call to the User Service**, preventing it from becoming a performance bottleneck.

3.  **Order Placement (Synchronous Path)**: The client sends a `POST /orders` request to the API Gateway.
    -   The Gateway validates the token and forwards the request to the **Order Service**, passing the validated `user_id` in a secure internal header (`user-id`).
    -   The Order Service receives the request. Before committing to the order, it must verify product availability and pricing in real-time. It performs a **synchronous, blocking HTTP `GET` call** to the Product Service's internal endpoint (`GET /products/{product_id}`). This is a deliberate, necessary coupling; an order cannot be created for a product that doesn't exist or is out of stock.
    -   If the Product Service returns a successful response, the Order Service calculates the total price, saves a new order record to its private `order_db`, and immediately returns a `201 Created` response to the client. The user-facing portion of the transaction is now complete.

4.  **Inventory Update (Asynchronous Path)**: Immediately after persisting the order, the **Order Service** publishes an `OrderCreated` event to a durable queue in **RabbitMQ**.
    -   The **Product Service** runs a background consumer thread that is perpetually connected to this queue. It consumes the `OrderCreated` event.
    -   Upon receiving the message, it executes a database transaction with `SELECT ... FOR UPDATE` to lock the product rows, and then decrements the stock quantity in its `product_db`. This happens completely out-of-band from the user's initial request.

## 3. Key Architectural Patterns & Justifications

### 3.1. The API Gateway Pattern
-   **Security**: Acts as a chokepoint for all incoming traffic, allowing for centralized authentication and authorization logic.
-   **Abstraction & Decoupling**: The client is decoupled from the internal service topology. Internal services can be refactored or replaced without affecting the client.
-   **Cross-Cutting Concerns**: Ideal location for managing rate limiting, request logging, and distributed tracing.

### 3.2. Asynchronous Event-Driven Communication via Message Broker
-   **Resilience & Fault Tolerance**: An outage in the `Product Service` **does not** block or fail the user-facing order creation process. Messages persist in RabbitMQ and will be processed upon service recovery.
-   **Temporal Decoupling & Scalability**: The `Order Service` and `Product Service` can be deployed, scaled, and maintained independently.
-   **Responsiveness**: The user receives immediate order confirmation without waiting for slower, downstream processes.

### 3.3. Database per Service
-   **Data Ownership & Encapsulation**: Each service is the single source of truth for its own data, accessible only via its public API contract.
-   **Independent Evolution**: Prevents the "shared database integration" anti-pattern, allowing teams to evolve their schemas independently.
-   **Technology Autonomy**: Enables each service to choose the best data storage technology for its specific needs.

## 4. Technology Stack & Rationale

| Category           | Technology       | Rationale                                                                                                                                                                            |
|--------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Orchestration**  | Docker Compose   | Provides a simple, declarative way to define, build, network, and run the entire multi-container application stack for development and testing.                                        |
| **Frameworks**     | FastAPI          | Chosen for high performance, native async support, and automatic data validation which hardens services against invalid inputs.                                                       |
| **Databases**      | PostgreSQL       | A robust, feature-rich relational database ideal for enforcing the structured data integrity required by users, products, and orders.                                                  |
| **Message Broker** | RabbitMQ         | A mature, reliable message broker supporting durable queues and guaranteed message delivery, ideal for critical business events.                                                     |
| **Service Comm.**  | HTTPX            | A modern, async-capable HTTP client for Python used for fast, non-blocking synchronous communication between services.                                                               |
| **Testing**        | Pytest           | The standard for Python testing, used for an end-to-end (E2E) integration test that simulates a real user journey across the entire system.                                           |

## 5. Running the System: Manual Operation Guide

This section provides a complete, step-by-step guide for launching and initializing the system. Following this controlled sequence is crucial for a successful startup.

### Prerequisites
-   Docker and Docker Compose (V2+)

### Step-by-Step Initialization

#### Step 1: Clean Up and Start Core Infrastructure
First, ensure a clean environment by removing any previous containers and volumes. Then, start only the database and message broker.
```bash
# From the root of this solution directory (backend-engineer/problems/problem-2/)
docker compose down -v
docker compose up -d postgres rabbitmq
```

#### Step 2: Wait for PostgreSQL to Become Healthy
The application services depend on the database. Do not proceed until the PostgreSQL container is fully initialized and ready.
```bash
# Run this command until the STATUS for the 'postgres' container shows '(healthy)'
docker compose ps
```
This may take 10-20 seconds on the first run.

#### Step 3: Create Databases
With PostgreSQL running, connect to it to create the dedicated databases for each service.
```bash
docker compose exec postgres createdb -U interview_user user_db
docker compose exec postgres createdb -U interview_user product_db
docker compose exec postgres createdb -U interview_user order_db
```

#### Step 4: Manually Initialize Table Schemas
The application services require their database tables to be created before they can function. Run the following commands to manually build the schema in each database.
```bash
# Create tables for the User Service
docker compose run --rm user_service python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Create tables for the Product Service
docker compose run --rm product_service python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Create tables for the Order Service
docker compose run --rm order_service python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

#### Step 5: Launch All Application Services
With the infrastructure and database schemas fully prepared, you can now start all the application services.
```bash
docker compose up --build -d
```
After about 10 seconds, the entire system will be running and ready to accept requests.

## 6. API Interaction & Validation Walkthrough

All interactions must be directed to the API Gateway on port `8000`.

#### Step 1: Register a New User
```bash
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{
    "email": "engineer@ragworks.ai",
    "password": "a-strong-password-123"
}'
```
**Expected Response:** `201 Created` with the new user's JSON object (e.g., `{"email":"engineer@ragworks.ai","id":1}`).

#### Step 2: Authenticate and Capture JWT
```bash
# Execute this and copy the `access_token` value from the response
curl -X POST "http://localhost:8000/token" \
-H "Content-Type: application/json" \
-d '{
    "email": "engineer@ragworks.ai",
    "password": "a-strong-password-123"
}'

# Store the token in a shell variable for convenience
export TOKEN="<paste-your-token-here>"
```
**Expected Response:** `200 OK` with the JWT access token.

#### Step 3: Create a Product
```bash
curl -X POST "http://localhost:8000/products" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "name": "Quantum Mechanical Keyboard",
    "price": 249.99,
    "quantity": 50
}'
```
**Expected Response:** `201 Created` with the full product object. **Note the `id` of the product.**

#### Step 4: Place an Order
```bash
# Replace '1' in "product_id" with the actual ID from the previous step
curl -X POST "http://localhost:8000/orders" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "items": [
        {
            "product_id": 1,
            "quantity": 3
        }
    ]
}'
```
**Expected Response:** `201 Created` with the order details.

#### Step 5: Verify Asynchronous Inventory Update
Wait a few seconds for the event to be processed in the background. Then, fetch the product to confirm its stock has been updated.
```bash
# Wait ~5 seconds. Replace '1' with the product ID.
curl -X GET "http://localhost:8000/products/1"
```
**Expected Response:** `200 OK` with the product details. The `quantity` field must be **47**.
```json
{
  "name": "Quantum Mechanical Keyboard",
  "price": 249.99,
  "id": 1,
  "quantity": 47
}
```
Observing this change from **50** to **47** provides definitive proof that the entire distributed, event-driven workflow has completed successfully.

## 7. Automated Test Execution

For rapid validation, an end-to-end test script is provided. This script automates the entire system lifecycle: build, orchestrated startup, database initialization, API testing, and teardown.

### Prerequisites
-   A local Python environment with `pytest` and `httpx` installed (`pip install pytest httpx`).

### Execution
From the root of this solution directory, execute:
```bash
./run_coverage_test.sh
```
A **`1 passed`** result from this script is conclusive evidence that the entire distributed system is functioning correctly as designed.