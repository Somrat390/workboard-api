
from app.models import Organization, OrganizationMembership, User
from app.services.organization import (
    generate_unique_slug,
    create_organization,
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
