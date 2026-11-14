
from app.models import Organization, OrganizationMembership, User
from app.services.organization import (
    generate_unique_slug,
    create_organization,
    get_user_organizations,
)

def test_generate_unique_slug(db):
    # First organization
    first_organization = Organization(
        name="Acme Technologies",
        slug="acme-technologies",
    )

    db.add(first_organization)
    db.commit()

    # Generate a slug for another organization
    slug = generate_unique_slug(
        "Acme Technologies",
        db,
    )

    assert slug == "acme-technologies-2"



def test_generate_unique_slug_when_no_collision(db):
    slug = generate_unique_slug(
        "Acme Technologies",
        db,
    )

    assert slug == "acme-technologies"


def test_generate_unique_slug_with_multiple_collisions(db):
    db.add_all([
        Organization(
            name="Acme Technologies",
            slug="acme-technologies",
        ),
        Organization(
            name="Acme Technologies",
            slug="acme-technologies-2",
        ),
    ])
    db.commit()

    slug = generate_unique_slug(
        "Acme Technologies",
        db,
    )

    assert slug == "acme-technologies-3"



def test_create_organization_with_owner(db):
    user = User(
        full_name="Test User",
        email="owner@example.com",
        hashed_password="fake-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    organization = create_organization(
        name="Acme Technologies",
        user_id=user.id,
        db=db,
    )

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id
            == organization.id
        )
        .first()
    )

    assert organization.name == "Acme Technologies"
    assert organization.slug == "acme-technologies"

    assert membership is not None
    assert membership.user_id == user.id
    assert membership.role == "owner"



def test_get_user_organizations(db):
    # Create two users
    user1 = User(
        full_name="User One",
        email="user1@example.com",
        hashed_password="fake-hash",
    )

    user2 = User(
        full_name="User Two",
        email="user2@example.com",
        hashed_password="fake-hash",
    )

    db.add_all([user1, user2])
    db.commit()

    # Create three organizations
    organization1 = Organization(
        name="Acme Technologies",
        slug="acme-technologies",
    )

    organization2 = Organization(
        name="Tech Solutions",
        slug="tech-solutions",
    )

    organization3 = Organization(
        name="Global Research",
        slug="global-research",
    )

    db.add_all([
        organization1,
        organization2,
        organization3,
    ])
    db.commit()

    # User 1 belongs to organizations 1 and 2
    # User 2 belongs to organization 3
    db.add_all([
        OrganizationMembership(
            user_id=user1.id,
            organization_id=organization1.id,
            role="owner",
        ),
        OrganizationMembership(
            user_id=user1.id,
            organization_id=organization2.id,
            role="member",
        ),
        OrganizationMembership(
            user_id=user2.id,
            organization_id=organization3.id,
            role="owner",
        ),
    ])
    db.commit()

    # Retrieve User 1's organizations
    organizations = get_user_organizations(
        user_id=user1.id,
        db=db,
    )

    organization_names = {
        organization.name
        for organization in organizations
    }

    assert len(organizations) == 2

    assert organization_names == {
        "Acme Technologies",
        "Tech Solutions",
    }

    assert "Global Research" not in organization_names
