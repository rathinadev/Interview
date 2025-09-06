from fastapi.testclient import TestClient

def get_auth_headers(client: TestClient, username: str = "testprojectuser", password: str = "password123"):
    """Helper function to register and log in a user, returning auth headers."""
    client.post("/auth/register", json={"username": username, "email": f"{username}@example.com", "password": password})
    login_response = client.post("/auth/token", data={"username": username, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_and_get_project(client: TestClient):
    headers = get_auth_headers(client)
    
    # Create project
    response_create = client.post("/projects", json={"name": "My First Project"}, headers=headers)
    assert response_create.status_code == 201
    project_data = response_create.json()
    assert project_data["name"] == "My First Project"
    project_id = project_data["id"]

    # Get the project by ID
    response_get = client.get(f"/projects/{project_id}", headers=headers)
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "My First Project"

def test_unauthorized_project_access(client: TestClient):
    # User 1 creates a project
    headers1 = get_auth_headers(client, username="user1")
    response_create = client.post("/projects", json={"name": "User 1 Project"}, headers=headers1)
    project_id = response_create.json()["id"]

    # User 2 tries to access it
    headers2 = get_auth_headers(client, username="user2")
    response_get = client.get(f"/projects/{project_id}", headers=headers2)
    
    # Should be forbidden
    assert response_get.status_code == 403

def test_create_task_for_project(client: TestClient):
    headers = get_auth_headers(client)
    
    # Create project
    response_project = client.post("/projects", json={"name": "Project for Tasks"}, headers=headers)
    project_id = response_project.json()["id"]

    # Create task
    response_task = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "My first task"},
        headers=headers
    )
    assert response_task.status_code == 201
    task_data = response_task.json()
    assert task_data["title"] == "My first task"
    assert task_data["project_id"] == project_id

def test_update_project(client: TestClient):
    headers = get_auth_headers(client, username="updateuser")
    
    # Create a project first
    response_create = client.post("/projects", json={"name": "Old Name", "description": "Old Desc"}, headers=headers)
    project_id = response_create.json()["id"]

    # Now update it
    response_update = client.put(
        f"/projects/{project_id}",
        json={"name": "New Name", "description": "New Desc"},
        headers=headers
    )
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["name"] == "New Name"
    assert data["description"] == "New Desc"
    assert data["id"] == project_id

def test_delete_project(client: TestClient):
    headers = get_auth_headers(client, username="deleteuser")

    # Create a project first
    response_create = client.post("/projects", json={"name": "To Be Deleted"}, headers=headers)
    project_id = response_create.json()["id"]

    # Delete it
    response_delete = client.delete(f"/projects/{project_id}", headers=headers)
    assert response_delete.status_code == 204

    # Verify it's gone
    response_get = client.get(f"/projects/{project_id}", headers=headers)
    assert response_get.status_code == 404

def test_get_nonexistent_project_404(client: TestClient):
    headers = get_auth_headers(client, username="404user")
    
    # Try to get a project that doesn't exist
    response_get = client.get("/projects/99999", headers=headers)
    assert response_get.status_code == 404

def test_task_lifecycle_update_and_delete(client: TestClient):
    """Tests the full lifecycle: creating, updating, and deleting a task."""
    headers = get_auth_headers(client, username="tasklifecycleuser")
    
    # Create a project
    project_response = client.post("/projects", json={"name": "Task Lifecycle Project"}, headers=headers)
    project_id = project_response.json()["id"]

    # Create a task in that project
    task_response_create = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Original Task Title", "status": "todo"},
        headers=headers
    )
    assert task_response_create.status_code == 201
    task_id = task_response_create.json()["id"]

    # Update the task
    task_response_update = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Task Title", "status": "done"},
        headers=headers
    )
    assert task_response_update.status_code == 200
    assert task_response_update.json()["title"] == "Updated Task Title"
    assert task_response_update.json()["status"] == "done"

    # Delete the task
    task_response_delete = client.delete(f"/tasks/{task_id}", headers=headers)
    assert task_response_delete.status_code == 204

    # Verify it's gone
    task_response_get = client.get(f"/tasks/{task_id}", headers=headers)
    assert task_response_get.status_code == 404


def test_unauthorized_task_modification_403(client: TestClient):
    """Tests that a user cannot modify a task they don't own."""
    # User 1 creates a project and a task
    headers_user1 = get_auth_headers(client, username="user1_owner")
    project_res = client.post("/projects", json={"name": "User 1 Project"}, headers=headers_user1)
    project_id = project_res.json()["id"]
    task_res = client.post(f"/projects/{project_id}/tasks", json={"title": "User 1 Task"}, headers=headers_user1)
    task_id = task_res.json()["id"]

    # User 2 logs in
    headers_user2 = get_auth_headers(client, username="user2_attacker")

    # User 2 tries to delete User 1's task
    response_delete = client.delete(f"/tasks/{task_id}", headers=headers_user2)
    assert response_delete.status_code == 403 # Should be Forbidden