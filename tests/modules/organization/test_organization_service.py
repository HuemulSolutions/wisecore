import pytest

from src.modules.organization.service import OrganizationService


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_persists_entity(db_session):
    """Test that creating an organization persists it correctly in the database."""
    service = OrganizationService(db_session)

    organization = await service.create_organization(
        name="Acme Corp",
        description="Testing organization",
    )

    assert organization.id is not None

    organizations = await service.get_all_organizations()
    assert len(organizations) == 1
    assert organizations[0].name == "Acme Corp"
    assert organizations[0].description == "Testing organization"


@pytest.mark.asyncio(loop_scope="session")
async def test_duplicate_organization_name_is_rejected(db_session):
    """Test that duplicate organization names are rejected."""
    service = OrganizationService(db_session)
    await service.create_organization(name="Acme Corp", description=None)

    with pytest.raises(ValueError):
        await service.create_organization(name="Acme Corp")


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_without_description(db_session):
    """Test creating organization without description (None as default)."""
    service = OrganizationService(db_session)

    organization = await service.create_organization(name="Minimal Org")

    assert organization.id is not None
    assert organization.name == "Minimal Org"
    assert organization.description is None

    organizations = await service.get_all_organizations()
    assert len(organizations) == 1
    assert organizations[0].description is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_with_empty_description(db_session):
    """Test creating organization with empty string as description."""
    service = OrganizationService(db_session)

    organization = await service.create_organization(
        name="Empty Desc Org", 
        description=""
    )

    assert organization.id is not None
    assert organization.name == "Empty Desc Org"
    assert organization.description == ""


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_empty_name_raises_error(db_session):
    """Test that creating organization with empty name raises ValueError."""
    service = OrganizationService(db_session)

    with pytest.raises(ValueError, match="Organization name cannot be empty"):
        await service.create_organization(name="")

    with pytest.raises(ValueError, match="Organization name cannot be empty"):
        await service.create_organization(name=None)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_organizations_empty_list(db_session):
    """Test getting all organizations when none exist."""
    service = OrganizationService(db_session)

    organizations = await service.get_all_organizations()

    assert isinstance(organizations, list)
    assert len(organizations) == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_organizations_multiple_entities(db_session):
    """Test getting all organizations with multiple entities."""
    service = OrganizationService(db_session)

    # Create multiple organizations
    org1 = await service.create_organization("Tech Corp", "Technology company")
    org2 = await service.create_organization("Finance Inc", "Financial services")
    org3 = await service.create_organization("Health Ltd")

    organizations = await service.get_all_organizations()

    assert len(organizations) == 3
    
    # Verify all organizations are returned
    org_names = [org.name for org in organizations]
    assert "Tech Corp" in org_names
    assert "Finance Inc" in org_names
    assert "Health Ltd" in org_names
    
    # Verify all have IDs
    for org in organizations:
        assert org.id is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_check_organization_exists_with_existing_organization(db_session):
    """Test checking if organization exists when it does exist."""
    service = OrganizationService(db_session)

    # Create organization
    organization = await service.create_organization("Existing Corp", "Test description")
    
    # Check if it exists (convert UUID to string)
    exists = await service.check_organization_exists(str(organization.id))
    
    assert exists is True


@pytest.mark.asyncio(loop_scope="session")
async def test_check_organization_exists_with_non_existing_organization(db_session):
    """Test checking if organization exists when it doesn't exist."""
    service = OrganizationService(db_session)
    from uuid import uuid4

    # Check with non-existing but valid UUID
    non_existing_uuid = str(uuid4())
    exists = await service.check_organization_exists(non_existing_uuid)
    
    assert exists is False


@pytest.mark.asyncio(loop_scope="session")
async def test_check_organization_exists_with_invalid_id_format(db_session):
    """Test checking organization exists with various invalid ID formats raises ValueError."""
    service = OrganizationService(db_session)

    # Test with different invalid formats
    invalid_ids = ["", "invalid-uuid", "123", "not-a-real-id", "abc-def-ghi"]
    
    for invalid_id in invalid_ids:
        with pytest.raises(ValueError, match="Invalid organization ID format"):
            await service.check_organization_exists(invalid_id)
    
    # Test with None specifically
    with pytest.raises(ValueError, match="Invalid organization ID format"):
        await service.check_organization_exists(None)


@pytest.mark.asyncio(loop_scope="session")
async def test_check_organization_exists_with_valid_uuid_format(db_session):
    """Test that valid UUID formats work correctly even if organization doesn't exist."""
    service = OrganizationService(db_session)
    from uuid import uuid4

    # Test with multiple valid UUIDs
    for _ in range(3):
        valid_uuid = str(uuid4())
        exists = await service.check_organization_exists(valid_uuid)
        assert exists is False  # Should return False, not raise error


@pytest.mark.asyncio(loop_scope="session")
async def test_check_organization_exists_uuid_string_conversion(db_session):
    """Test that UUID conversion works properly with different string formats."""
    service = OrganizationService(db_session)
    from uuid import uuid4

    # Create organization and test different UUID string representations
    organization = await service.create_organization("UUID Test Org", "Testing UUID conversion")
    org_id = organization.id
    
    # Test with string conversion
    exists = await service.check_organization_exists(str(org_id))
    assert exists is True
    
    # Test with uppercase UUID string
    exists = await service.check_organization_exists(str(org_id).upper())
    assert exists is True
    
    # Test with lowercase UUID string
    exists = await service.check_organization_exists(str(org_id).lower())
    assert exists is True


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_case_sensitive_names(db_session):
    """Test that organization names are case sensitive."""
    service = OrganizationService(db_session)

    # Create organizations with different cases
    org1 = await service.create_organization("ACME CORP")
    org2 = await service.create_organization("acme corp")
    org3 = await service.create_organization("Acme Corp")

    organizations = await service.get_all_organizations()
    assert len(organizations) == 3

    org_names = [org.name for org in organizations]
    assert "ACME CORP" in org_names
    assert "acme corp" in org_names
    assert "Acme Corp" in org_names


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_whitespace_handling(db_session):
    """Test organization creation with whitespace in names."""
    service = OrganizationService(db_session)

    # Test with leading/trailing spaces - these should be treated as different
    org1 = await service.create_organization(" Spaced Org ")
    org2 = await service.create_organization("Spaced Org")

    organizations = await service.get_all_organizations()
    assert len(organizations) == 2

    org_names = [org.name for org in organizations]
    assert " Spaced Org " in org_names
    assert "Spaced Org" in org_names


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_returns_correct_instance(db_session):
    """Test that create_organization returns the correct Organization instance."""
    service = OrganizationService(db_session)

    organization = await service.create_organization(
        name="Test Instance",
        description="Testing return instance"
    )

    # Verify it's the correct type and has expected attributes
    from src.modules.organization.models import Organization
    assert isinstance(organization, Organization)
    assert hasattr(organization, 'id')
    assert hasattr(organization, 'name')
    assert hasattr(organization, 'description')
    assert organization.name == "Test Instance"
    assert organization.description == "Testing return instance"


@pytest.mark.asyncio(loop_scope="session")
async def test_service_initialization(db_session):
    """Test that OrganizationService initializes correctly."""
    service = OrganizationService(db_session)

    assert service.session == db_session
    assert hasattr(service, 'organization_repo')
    assert service.organization_repo is not None
