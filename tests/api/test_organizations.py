from app.models import OrganizationMembership, Organization



def test_create_organization(client):
    # Register a user
    client.post(
        "/api/v1/users/",
        json={
            "full_name": "Organization Owner",
            "email": "owner@example.com",
            "password": "securepassword123",
        },
    )

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "owner@example.com",
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    # Create organization
    response = client.post(
        "/api/v1/organizations/",
        json={
            "name": "Acme Technologies",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Acme Technologies"
    assert data["slug"] == "acme-technologies"
    assert "id" in data
    assert "created_at" in data


def test_create_organization_without_token(client):
    response = client.post(
        "/api/v1/organizations/",
        json={
            "name": "Unauthorized Organization",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"



def test_organization_creator_becomes_owner(client, db):
    # Register user
    client.post(
        "/api/v1/users/",
        json={
            "full_name": "Organization Owner",
            "email": "owner@example.com",
            "password": "securepassword123",
        },
    )

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "owner@example.com",
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    # Create organization
    response = client.post(
        "/api/v1/organizations/",
        json={
            "name": "Acme Technologies",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    organization_id = response.json()["id"]

    # Check membership in database
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id
        )
        .first()
    )

    assert membership is not None
    assert membership.role == "owner"


def test_list_user_organizations(client):
    # Register User 1
    client.post(
        "/api/v1/users/",
        json={
            "full_name": "User One",
            "email": "user1@example.com",
            "password": "securepassword123",
        },
    )

    # Login User 1
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user1@example.com",
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # User 1 creates two organizations
    client.post(
        "/api/v1/organizations/",
        json={"name": "Acme Technologies"},
        headers=headers,
    )

    client.post(
        "/api/v1/organizations/",
        json={"name": "Tech Solutions"},
        headers=headers,
    )

    # Register User 2
    client.post(
        "/api/v1/users/",
        json={
            "full_name": "User Two",
            "email": "user2@example.com",
            "password": "securepassword123",
        },
    )

    # Login User 2
    login_response_2 = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user2@example.com",
            "password": "securepassword123",
        },
    )

    token_2 = login_response_2.json()["access_token"]

    # User 2 creates a separate organization
    client.post(
        "/api/v1/organizations/",
        json={"name": "Global Research"},
        headers={
            "Authorization": f"Bearer {token_2}",
        },
    )

    # User 1 requests their organizations
    response = client.get(
        "/api/v1/organizations/",
        headers=headers,
    )

    assert response.status_code == 200

    organizations = response.json()

    organization_names = {
        organization["name"]
        for organization in organizations
    }

    assert len(organizations) == 2

    assert organization_names == {
        "Acme Technologies",
        "Tech Solutions",
    }

    assert "Global Research" not in organization_names


def test_list_organizations_without_token(client):
    response = client.get("/api/v1/organizations/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"