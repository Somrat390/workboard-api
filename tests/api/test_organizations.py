from app.models import OrganizationMembership



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