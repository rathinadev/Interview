import httpx
import time
import pytest

API_GATEWAY_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def client():
    # A small delay to ensure all services are fully started
    time.sleep(10)
    with httpx.Client(base_url=API_GATEWAY_URL, timeout=30) as c:
        yield c

def test_full_e2commerce_flow(client: httpx.Client):
    # 1. Register a new user
    user_email = f"testuser_{int(time.time())}@example.com"
    user_pass = "a_secure_password123"
    reg_response = client.post("/register", json={"email": user_email, "password": user_pass})
    assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"
    print(f"User '{user_email}' registered successfully.")

    # 2. Log in to get an access token
    login_response = client.post("/token", json={"email": user_email, "password": user_pass})
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful, token obtained.")

    # 3. Create a product (as an authenticated user)
    product_payload = {"name": "Super Laptop", "price": 1299.99, "quantity": 20}
    product_response = client.post("/products", json=product_payload, headers=headers)
    assert product_response.status_code == 201, f"Product creation failed: {product_response.text}"
    product_id = product_response.json()["id"]
    print(f"Product 'Super Laptop' created with ID: {product_id}")

    # 4. Create an order for that product
    order_payload = {"items": [{"product_id": product_id, "quantity": 2}]}
    order_response = client.post("/orders", json=order_payload, headers=headers)
    assert order_response.status_code == 201, f"Order creation failed: {order_response.text}"
    order_data = order_response.json()
    assert order_data["status"] == "PENDING"
    assert order_data["total_price"] == 1299.99 * 2
    print(f"Order created successfully with ID: {order_data['id']}")
    
    # 5. (Implicit test) Check if stock was reduced.
    # We can't easily check RabbitMQ in this test, but we can check the product's state.
    time.sleep(5) # Give RabbitMQ and the consumer time to work
    product_check_response = client.get(f"/products/{product_id}")
    assert product_check_response.status_code == 200
    final_quantity = product_check_response.json()["quantity"]
    assert final_quantity == 18 # Initial quantity (20) - order quantity (2)
    print(f"Verified product quantity was reduced to {final_quantity}.")