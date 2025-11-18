import pytest
from uuid import uuid4

from src.modules.organization.service import OrganizationService
from src.modules.template.service import TemplateService


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_requires_existing_organization(db_session):
    org_service = OrganizationService(db_session)
    template_service = TemplateService(db_session)

    organization = await org_service.create_organization(
        name="WiseCore QA",
        description="Org for template testing",
    )

    template = await template_service.create_template(
        name="Quality Checklist",
        organization_id=str(organization.id),
        description="Template for QA flows",
    )

    assert template.id is not None
    assert str(template.organization_id) == str(organization.id)
    assert template.name == "Quality Checklist"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_fails_when_org_missing(db_session):
    template_service = TemplateService(db_session)

    with pytest.raises(ValueError):
        await template_service.create_template(
            name="Ghost Template",
            organization_id=str(uuid4()),
            description=None,
        )
