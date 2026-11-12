
from sqlalchemy.orm import Session

from app.models import Organization, OrganizationMembership
from app.core.utils import generate_slug


def generate_unique_slug(
    name: str,
    db: Session,
) -> str:
    base_slug = generate_slug(name) or "organization"
    slug = base_slug
    counter = 2

    while (
        db.query(Organization)
        .filter(Organization.slug == slug)
        .first()
        is not None
    ):
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug



def create_organization(
    name: str,
    user_id: int,
    db: Session,
) -> Organization:
    slug = generate_unique_slug(name, db)

    organization = Organization(
        name=name,
        slug=slug,
    )

    try:
        db.add(organization)
        db.flush()

        membership = OrganizationMembership(
            user_id=user_id,
            organization_id=organization.id,
            role="owner",
        )

        db.add(membership)
        db.commit()
        db.refresh(organization)

    except Exception:
        db.rollback()
        raise

    return organization



