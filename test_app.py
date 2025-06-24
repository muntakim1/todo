import pytest
from fastapi.testclient import TestClient
from main import app
from config.database import SessionLocal
from Todo.model.todo_model import Todo
from user.model.user_model import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_db():
    yield
    db = SessionLocal()
    db.query(Todo).delete()
    db.query(User).delete()
    db.commit()
    db.close()

# Helper to register a user
def register_user(username, email, password, is_admin=False):
    return client.post("/user/register", json={
        "username": username,
        "email": email,
        "password": password,
        "is_admin": is_admin
    })

# Helper to login and get token
def login_user(username_or_email, password):
    response = client.post("/user/token", data={"username": username_or_email, "password": password})
    return response.json().get("access_token")

# --- User Registration & Auth ---
def test_register_and_login():
    r = register_user("testuser", "testuser@email.com", "testpass")
    assert r.status_code == 200
    token = login_user("testuser", "testpass")
    assert token
    token2 = login_user("testuser@email.com", "testpass")
    assert token2

def test_unique_username_email():
    register_user("uniqueuser", "unique@email.com", "pass")
    r1 = register_user("uniqueuser", "other@email.com", "pass")
    r2 = register_user("otheruser", "unique@email.com", "pass")
    assert r1.status_code == 400
    assert r2.status_code == 400

# --- Todo CRUD ---
def test_todo_crud():
    register_user("todouser", "todouser@email.com", "todopass")
    token = login_user("todouser", "todopass")
    headers = {"Authorization": f"Bearer {token}"}
    # Create
    r = client.post("/todo/todos/", json={"title": "Test Todo"}, headers=headers)
    assert r.status_code == 200
    todo_id = r.json()["id"]
    # Read
    r = client.get("/todo/todos/", headers=headers)
    assert r.status_code == 200
    # Update
    r = client.patch(f"/todo/todos/{todo_id}", json={"completed": True}, headers=headers)
    assert r.status_code == 200
    assert r.json()["completed"] is True
    # Delete
    r = client.delete(f"/todo/todos/{todo_id}", headers=headers)
    assert r.status_code == 200

def test_todo_requires_auth():
    r = client.post("/todo/todos/", json={"title": "NoAuth"})
    assert r.status_code == 401
    r = client.get("/todo/todos/")
    assert r.status_code == 401
    r = client.patch("/todo/todos/1", json={"completed": True})
    assert r.status_code == 401
    r = client.delete("/todo/todos/1")
    assert r.status_code == 401

# --- Admin Only ---
def test_admin_can_see_and_delete_users():
    register_user("admin", "admin@email.com", "adminpass", is_admin=True)
    register_user("user1", "user1@email.com", "userpass")
    admin_token = login_user("admin", "adminpass")
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = client.get("/user/all", headers=headers)
    assert r.status_code == 200
    users = r.json()
    user_id = [u["id"] for u in users if u["username"] == "user1"][0]
    r = client.delete(f"/user/{user_id}", headers=headers)
    assert r.status_code == 200

def test_non_admin_cannot_see_or_delete_users():
    register_user("notadmin", "notadmin@email.com", "notadminpass")
    token = login_user("notadmin", "notadminpass")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/user/all", headers=headers)
    assert r.status_code == 403
    r = client.delete("/user/1", headers=headers)
    assert r.status_code == 403
