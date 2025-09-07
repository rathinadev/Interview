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

This section details the rationale behind the key design decisions, which are critical talking points for an architectural review.

### 3.1. The API Gateway Pattern
A custom API Gateway was built instead of exposing services directly to the internet.
-   **Security**: It acts as a chokepoint for all incoming traffic, allowing for centralized authentication and authorization logic. Internal services are not exposed publicly, dramatically reducing the attack surface.
-   **Abstraction & Decoupling**: The client is completely decoupled from the internal service topology. We can refactor, decompose, or replace internal services (e.g., splitting the Product Service into `Catalog` and `Inventory` services) without requiring a single change on the client-side.
-   **Cross-Cutting Concerns**: It is the ideal location to manage concerns that apply to all services, such as rate limiting, request logging, and instituting distributed tracing with correlation IDs.

### 3.2. Asynchronous Event-Driven Communication via Message Broker
The choice to use RabbitMQ for inventory updates is the cornerstone of the system's resilience.
-   **Resilience & Fault Tolerance**: An outage or significant slowdown in the `Product Service` **does not** block or fail the user-facing order creation process. Messages are safely persisted in RabbitMQ's durable queue and will be processed when the service recovers. This prevents cascading failures.
-   **Temporal Decoupling & Scalability**: The `Order Service` (the producer) does not need the `Product Service` (the consumer) to be running at the same time. This allows for independent deployments and maintenance windows. Furthermore, the `Product Service` can be scaled horizontally with more consumer instances to process a high volume of orders from the queue without any changes to the `Order Service`.
-   **Responsiveness**: The user receives an immediate confirmation of their order without waiting for slower, downstream processes like inventory updates, leading to a superior user experience.

### 3.3. Database per Service
This is a non-negotiable principle of this microservice design.
-   **Data Ownership & Encapsulation**: Each service is the single source of truth for its own data. No other service is allowed to access another service's database directly. Communication must happen via the service's public API contract.
-   **Independent Evolution**: This prevents the "shared database integration" anti-pattern. The Product team can change their database schema at will without coordinating with or breaking the Order or User teams.
-   **Technology Autonomy**: This pattern allows each team to choose the best data storage technology for their specific needs. While all services here use PostgreSQL for simplicity, the Product service could, for example, switch to a NoSQL database for its catalog without impacting the rest of the system.

## 4. Technology Stack & Rationale

| Category           | Technology       | Rationale                                                                                                                                                                            |
|--------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Orchestration**  | Docker Compose   | Provides a simple, declarative, and version-controllable way to define, build, network, and run the entire multi-container application stack for a development and testing environment.   |
| **Frameworks**     | FastAPI          | Chosen for its high performance, native async support (critical for an I/O-bound API Gateway), and automatic data validation which hardens services against invalid inputs.            |
| **Databases**      | PostgreSQL       | A robust, feature-rich relational database ideal for enforcing the structured data integrity required by users, products, and orders.                                                  |
| **Message Broker** | RabbitMQ         | A mature, reliable, and widely-used message broker that supports durable queues and guaranteed message delivery (via acknowledgements), making it ideal for critical business events. |
| **Service Comm.**  | HTTPX            | A modern, async-capable HTTP client for Python, used by the Gateway and Order Service for fast, non-blocking synchronous communication between services.                                |
| **Testing**        | Pytest           | The standard for Python testing. The solution is validated by an end-to-end (E2E) integration test that simulates a real user journey across the entire system.                        |

## 5. System Validation & Execution

The entire system is designed to be validated via a single, automated script.

### Prerequisites
-   Docker and Docker Compose (V2+)
-   A local Python environment with `pytest` and `httpx` installed (`pip install pytest httpx`).

### Automated Test Execution
This is the primary and definitive method for running and validating the entire architecture from a clean state. From the root of this solution directory (`backend-engineer/problems/problem-2/`), execute:

```bash
./run_coverage_test.sh
```
This script automates the full system lifecycle:
1.  **Cleanup**: Tears down any pre-existing containers, networks, and volumes.
2.  **Build & Start**: Builds fresh Docker images for all services and starts the entire stack, respecting the `depends_on` and `healthcheck` directives to ensure a stable startup order.
3.  **Database & Schema Initialization**: The script waits for PostgreSQL to be healthy, then executes `docker compose exec` to create the required databases. The services themselves handle the creation of their own tables via an `@app.on_event("startup")` hook for robustness.
4.  **E2E Test Execution**: Runs a "black box" integration test from the host machine against the public API Gateway. The test validates the full user flow: registration, login, product creation, order placement, and waits to verify that the asynchronous inventory update was successfully processed.
5.  **Teardown**: Gracefully stops and removes all containers and associated resources.

A **`1 passed`** result from this script is the conclusive evidence that the entire distributed system is functioning correctly as designed.

## 6. Manual Operation & Validation

This section provides a complete guide for manually launching, initializing, inspecting, and testing the system. These steps are automated by the `run_coverage_test.sh` script but are documented here for direct, hands-on validation and exploration.

### 6.1. System Launch & Initialization

#### Step 1: Launch All Services
From the root of this solution directory, build and start all containers in detached mode:
```bash
docker compose up --build -d
```
At this point, all containers will be running, but the application services will be in a waiting state, unable to fully initialize until their databases are available.

#### Step 2: Wait for PostgreSQL Healthcheck
Before proceeding, ensure the PostgreSQL container is fully initialized and ready to accept connections. The built-in healthcheck will manage this. You can monitor its status:
```bash
# Wait until the STATUS column for the postgres container shows 'healthy'
docker compose ps
```
This may take 10-20 seconds on the first run.

#### Step 3: Create Databases
With PostgreSQL healthy, execute the following commands to create the dedicated databases for each service:
```bash
docker compose exec postgres createdb -U interview_user user_db
docker compose exec postgres createdb -U interview_user product_db
docker compose exec postgres createdb -U interview_user order_db
```

#### Step 4: Apply Table Schemas
The application services are responsible for managing their own schemas. Trigger this initialization by running a one-off, temporary container for each service. This command executes the `init_db()` function defined in each service's startup logic.
```bash
docker compose run --rm user_service python -c "from app.database import init_db; init_db()"
docker compose run --rm product_service python -c "from app.database import init_db; init_db()"
docker compose run --rm order_service python -c "from app.database import init_db; init_db()"
```
After these commands complete, the system is fully initialized and ready for requests.

### 6.2. System Inspection Points

While the system is running, the following endpoints provide visibility into its internal state:

-   **Aggregated Logs:** For a real-time, color-coded log stream from all services, which is invaluable for observing inter-service communication:
    ```bash
    docker compose logs -f
    ```
-   **RabbitMQ Management Console:** To visually inspect the message queues, exchanges, and message flow:
    -   **URL:** `http://localhost:15672`
    -   **Credentials:** `guest` / `guest`
    -   *Navigate to the "Queues" tab to observe the `order_created_queue`.*

### 6.3. API Interaction Walkthrough (`curl`)

All interactions must be directed to the API Gateway.

#### Step 1: Register a New User
```bash
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{
    "email": "engineer@ragworks.ai",
    "password": "a-strong-password-123"
}'
```
**Expected Response:** `201 Created` with the new user's JSON object.

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
**Expected Response:** `201 Created` with the order details. The system responds immediately, confirming the order is `PENDING`. At this point, you can observe the message being published and consumed in the RabbitMQ UI and the Docker logs.

#### Step 5: Verify Asynchronous Inventory Update
This is the final validation. Wait a few seconds for the event to be processed.
```bash
# Wait ~5 seconds. Replace '1' with the product ID.
curl -X GET "http://localhost:8000/products/1"
```
**Expected Response:** `200 OK` with the product details. The `quantity` field must reflect the change from the asynchronous update.
```json
{
  "name": "Quantum Mechanical Keyboard",
  "price": 249.99,
  "id": 1,
  "quantity": 47
}
```
Observing the `quantity` change from **50** to **47** provides definitive proof that the entire distributed, event-driven workflow has completed successfully.

## 7. Codebase & Implementation Deep Dive

A consistent, predictable structure is applied across all services to promote maintainability and reduce cognitive load for developers. This section details the internal structure of a representative service, the `product_service`.

### 7.1. Service Directory Structure (`product_service/`)

```
product_service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application, startup events, and API route definitions.
│   ├── crud.py          # Data Access Object (DAO) layer for all database interactions.
│   ├── database.py      # SQLAlchemy engine, session management, and table initialization.
│   ├── models.py        # Declarative SQLAlchemy ORM models (the single source of truth for the schema).
│   └── pika_client.py   # All RabbitMQ consumer logic (connection, channel, queue, and callback).
└── Dockerfile           # Multi-stage Docker build for a lean, production-ready image.
```

### 7.2. Key Implementation Details

-   **Dependency Management:** All Python dependencies are managed in a single, root-level `requirements.txt` file and installed during the Docker build process. This ensures that all services are built and tested against a consistent set of library versions.
-   **Configuration Management:** Configuration is injected into each container via environment variables defined in `docker-compose.yml`. This follows the 12-Factor App methodology, separating config from code. A shared `settings.py` using `pydantic-settings` provides a typed, validated interface to these environment variables.
-   **Shared Code (`shared/`):** To avoid code duplication and ensure consistency, a `shared` directory contains common Pydantic schemas. This guarantees that the data contracts between the services (e.g., the structure of a `Product`) are consistent and validated on both the client and server sides of an internal API call.
-   **Asynchronous Consumer Logic:** The `product_service`'s RabbitMQ consumer is started in a separate, daemonized background thread during the FastAPI `startup` event. This is a simple yet effective pattern for running a long-lived background task alongside a web server in a single container, suitable for this application's scale.

## 8. Error Handling & Resilience Strategy

In a distributed system, partial failures are inevitable. This architecture is designed to handle them gracefully.

-   **Gateway Level:** If a downstream service (e.g., `Order Service`) is unavailable or returns a 5xx error, the API Gateway will propagate a `503 Service Unavailable` or the relevant error code back to the client. It does not crash; it reports the failure of a dependency.
-   **Synchronous Call Failure:** The `Order Service`'s synchronous `GET` call to the `Product Service` is wrapped in a `try...except` block. If the `Product Service` is down, `httpx` will raise an exception. The `Order Service` catches this and returns a meaningful error to the user (e.g., "Product service is unavailable"), preventing the exception from crashing the order creation process.
-   **Asynchronous Consumer Failure (Inventory Update):**
    -   **Connection Failure:** The RabbitMQ consumer (`pika_client.py`) is wrapped in a `while True` loop with exponential backoff. If the connection to RabbitMQ is lost, it will continuously attempt to reconnect, ensuring it can resume processing messages once the broker is available again.
    -   **Message Processing Failure (Poison Pill Mitigation):** The `on_message_received` callback includes a broad `try...except` block. If an individual message causes an unhandled exception during processing, the error is logged, and the message is **still acknowledged (`ch.basic_ack`)**. This is a deliberate choice to prevent a single "poison pill" message from blocking the queue and halting all subsequent inventory updates.
    -   **Production Improvement (Dead-Letter Queue):** For a production-grade system, the next logical step would be to configure a **Dead-Letter Queue (DLQ)** in RabbitMQ. Instead of just logging the error, the consumer would negatively acknowledge (`nack`) the poison pill message, causing RabbitMQ to automatically reroute it to a separate DLQ for later inspection and manual intervention by an engineer, without halting the processing of valid messages.

## 9. Architectural Trade-offs & Known Limitations

No architecture is without trade-offs. The decisions made here were optimized for resilience and scalability, with the following implications:

-   **Eventual Consistency:** This is the most significant trade-off. Because inventory updates are asynchronous, there is a brief consistency window (typically milliseconds) between when an order is confirmed and when the inventory level is updated in the `product_db`. During this window, it is theoretically possible for the system to sell an item that just went out of stock. For most e-commerce applications, this is an acceptable trade-off for the massive gains in system resilience and performance. More complex patterns like the Saga pattern could be used to manage rollbacks if strict consistency were required.
-   **Lack of Distributed Transactions:** The architecture intentionally avoids complex and brittle two-phase commit protocols for distributed transactions. Instead, it relies on the principle of choreography and compensating actions. If the inventory update fails, the current implementation logs an error. A more advanced implementation would publish an `InventoryUpdateFailed` event, which another service could consume to trigger a compensating action (e.g., flag the order for review, notify the user).
-   **Test Suite Focus:** The validation strategy prioritizes end-to-end integration testing. While individual unit tests could be added for complex business logic within each service, the E2E test provides the highest value by proving that the entire system, with all its complex interactions, functions correctly as a whole.

## 10. Potential Future Improvements

This architecture provides a strong foundation. Given additional time, the following production-hardening improvements would be considered:

-   **Distributed Tracing:** Implement a tracing solution like OpenTelemetry or Jaeger. The API Gateway would generate a `correlation-id` for each incoming request and propagate it through all subsequent service calls and event messages. This is invaluable for debugging and performance monitoring in a complex distributed system.
-   **Configuration & Secret Management:** Move sensitive configuration (like `JWT_SECRET_KEY` and database passwords) out of environment variables and into a secure secret management system like HashiCorp Vault or AWS Secrets Manager.
-   **Service Discovery:** For a more dynamic environment (e.g., Kubernetes), replace hardcoded service URLs in environment variables with a proper service discovery mechanism like Consul or CoreDNS.
-   **CI/CD Pipelines:** Implement separate, independent CI/CD pipelines for each microservice, allowing any service to be built, tested, and deployed to production without requiring a coordinated "big bang" release of the entire system.
