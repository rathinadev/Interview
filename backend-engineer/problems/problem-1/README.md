# Problem 1: Task Management API Solution

This project is a RESTful API for a task management system, built with FastAPI, PostgreSQL, and SQLAlchemy. It includes user authentication, CRUD operations for projects and tasks, and a full suite of automated tests.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8+
- Docker and Docker Compose
- An active internet connection to pull Docker images

## 🚀 Setup and Installation

### 1. Start the Infrastructure

All required services (PostgreSQL, Redis, etc.) run in Docker containers.

First, you need to create a shared Docker network for the project:
```bash
docker network create interview_network
```

Then, navigate to the `docker-compose` directory at the root of the interview repository and start the backend services:
```bash
# From the repository root
cd ../../../docker-compose/  # Adjust path as needed
./start-backend.sh
```
*Note: Make sure the `start-backend.sh` script uses the modern `docker compose` (with a space) command for compatibility.*

### 2. Set Up the Python Environment

Navigate back to this project directory (`problem-1-solution/`).

Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

Apply the database schema to the running PostgreSQL container using Alembic:
```bash
alembic upgrade head
```

## ▶️ Running the Application

To start the API server, run the following command from the project root:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### API Documentation

Interactive API documentation (Swagger UI) is automatically generated and can be accessed at:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

## 🧪 Running the Tests

To run the full test suite, use `pytest`:
```bash
pytest
```

To run the tests and view a test coverage report (requires `pip install pytest-cov`):
```bash
pytest --cov=app
```