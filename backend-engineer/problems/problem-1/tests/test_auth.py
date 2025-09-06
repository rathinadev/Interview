from fastapi.testclient import TestClient
import random

def test_register_user(client: TestClient):
    username = f"testuser{random.randint(1, 100000)}"
    email = f"{username}@example.com"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "hashed_password" not in data

def test_login(client: TestClient):
    # First, create a user to log in with
    username = f"loginuser{random.randint(1, 100000)}"
    email = f"{username}@example.com"
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": "testpassword"},
    )

    # Now, try to log in
    response = client.post(
        "/auth/token",
        data={"username": username, "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"