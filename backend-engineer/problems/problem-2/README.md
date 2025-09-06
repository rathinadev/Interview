# Problem 2: Microservice Architecture Solution

This project implements a microservice-based architecture for an e-commerce system. It consists of four main services: an API Gateway, a User Service, a Product Service, and an Order Service.

## Architecture Overview

- **API Gateway**: The single public entry point, responsible for routing requests and validating JWTs.
- **User Service**: Manages user registration and is the sole issuer of JWT authentication tokens.
- **Product Service**: Manages the product catalog and inventory levels.
- **Order Service**: Handles order creation and business logic.
- **Asynchronous Communication**: The Order Service and Product Service are decoupled using RabbitMQ. When an order is created, an `OrderCreated` event is published, which the Product Service consumes to update inventory.
- **Separate Databases**: Each service owns its own PostgreSQL database, adhering to microservice best practices.

## Prerequisites

- Docker and Docker Compose

## 🚀 Running the System

### 1. Build and Start All Services

From the root of this project directory, run the following command. This will build the Docker images for each service and start them in the background.

```bash
docker compose up --build -d
```

### 2. Create Databases

The services require their respective databases to be created before they can start properly. Run these commands:

```bash
docker compose exec postgres createdb -U interview_user user_db
docker compose exec postgres createdb -U interview_user product_db
docker compose exec postgres createdb -U interview_user order_db
```
The services will automatically create their own tables upon startup.

### 3. Check Service Health

You can view the status of all running containers with:
```bash
docker compose ps
```

To view the logs from all services in real-time:
```bash
docker compose logs -f
```

## 🧪 Running the End-to-End Test

An end-to-end test is provided to validate the entire system flow.

### Setup

Ensure you have `pytest` and `httpx` installed in a local Python environment:
```bash
pip install pytest httpx
```

### Execute Test

Run the test suite from the project root:
```bash
pytest tests/
```
The test simulates a full user journey: registration, login, product creation, order creation, and verifies that the inventory was updated asynchronously via the message queue.

## 🛠️ Accessing Services

- **API Gateway**: `http://localhost:8000` (All public traffic goes here)
- **RabbitMQ Management UI**: `http://localhost:15672` (user: `guest`, pass: `guest`)