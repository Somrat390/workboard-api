from app.models import User
from app.core.security import verify_password


def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "SecurePassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True

    assert "password" not in data
    assert "hashed_password" not in data



def test_create_user_with_duplicate_email(client):
    user_data = {
        "full_name": "Test User",
        "email": "duplicate@example.com",
        "password": "SecurePassword123",
    }

    # First registration should succeed
    first_response = client.post(
        "/api/v1/users/",
        json=user_data,
    )

    assert first_response.status_code == 201

    # Second registration with the same email should fail
    second_response = client.post(
        "/api/v1/users/",
        json=user_data,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"

def test_create_user_with_invalid_email(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Test User",
            "email": "invalid-email",
            "password": "SecurePassword123",
        },
    )

    assert response.status_code == 422


def test_create_user_with_short_password(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Test User",
            "email": "short@example.com",
            "password": "12345",
        },
    )

    assert response.status_code == 422



def test_user_password_is_hashed(client, db):
    password = "SecurePassword123"

    response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Security Test",
            "email": "security@example.com",
            "password": password,
        },
    )

    assert response.status_code == 201

    user = db.query(User).filter(
        User.email == "security@example.com"
    ).first()

    assert user is not None
    assert user.hashed_password != password
    assert verify_password(password, user.hashed_password)
    assert not verify_password("WrongPassword123", user.hashed_password)



def test_get_users(client):
    # Create a user first
    client.post(
        "/api/v1/users/",
        json={
            "full_name": "List Test",
            "email": "list@example.com",
            "password": "SecurePassword123",
        },
    )

    # Retrieve all users
    response = client.get("/api/v1/users/")

    assert response.status_code == 200

    users = response.json()

    assert len(users) == 1
    assert users[0]["email"] == "list@example.com"
    assert "hashed_password" not in users[0]
    assert "password" not in users[0]