import pytest
from uuid import uuid4

from src.modules.organization.models import Organization
from src.modules.organization.repository import OrganizationRepo


@pytest.mark.asyncio(loop_scope="session")
async def test_organization_repo_initialization(db_session):
    """Test that OrganizationRepo initializes correctly."""
    repo = OrganizationRepo(db_session)
    
    assert repo.session == db_session
    assert repo.model == Organization


@pytest.mark.asyncio(loop_scope="session")
async def test_add_organization(db_session):
    """Test adding an organization using the repository."""
    repo = OrganizationRepo(db_session)
    
    organization = Organization(
        name="Test Organization",
        description="A test organization"
    )
    
    result = await repo.add(organization)
    
    assert result.id is not None
    assert result.name == "Test Organization"
    assert result.description == "A test organization"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_id(db_session):
    """Test retrieving an organization by ID."""
    repo = OrganizationRepo(db_session)
    
    # Create and add organization
    organization = Organization(
        name="Retrievable Org",
        description="For testing retrieval"
    )
    saved_org = await repo.add(organization)
    await db_session.commit()
    
    # Retrieve by ID
    retrieved = await repo.get_by_id(saved_org.id)
    
    assert retrieved is not None
    assert retrieved.id == saved_org.id
    assert retrieved.name == "Retrievable Org"
    assert retrieved.description == "For testing retrieval"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_id_nonexistent(db_session):
    """Test retrieving a non-existent organization returns None."""
    repo = OrganizationRepo(db_session)
    
    nonexistent_id = uuid4()
    result = await repo.get_by_id(nonexistent_id)
    
    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_name(db_session):
    """Test retrieving an organization by name."""
    repo = OrganizationRepo(db_session)
    
    # Create and add organization
    organization = Organization(
        name="Unique Name Org",
        description="For testing name retrieval"
    )
    await repo.add(organization)
    await db_session.commit()
    
    # Retrieve by name
    retrieved = await repo.get_by_name("Unique Name Org")
    
    assert retrieved is not None
    assert retrieved.name == "Unique Name Org"
    assert retrieved.description == "For testing name retrieval"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_name_nonexistent(db_session):
    """Test retrieving a non-existent organization by name returns None."""
    repo = OrganizationRepo(db_session)
    
    result = await repo.get_by_name("Non-existent Organization")
    
    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_name_case_sensitive(db_session):
    """Test that name retrieval is case sensitive."""
    repo = OrganizationRepo(db_session)
    
    # Create organization with specific case
    organization = Organization(name="CaseSensitive Org")
    await repo.add(organization)
    await db_session.commit()
    
    # Test exact match
    exact_match = await repo.get_by_name("CaseSensitive Org")
    assert exact_match is not None
    
    # Test different cases
    lower_case = await repo.get_by_name("casesensitive org")
    assert lower_case is None
    
    upper_case = await repo.get_by_name("CASESENSITIVE ORG")
    assert upper_case is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_organizations(db_session):
    """Test retrieving all organizations."""
    repo = OrganizationRepo(db_session)
    
    # Create multiple organizations
    orgs = [
        Organization(name="Org 1", description="First org"),
        Organization(name="Org 2", description="Second org"),
        Organization(name="Org 3")
    ]
    
    for org in orgs:
        await repo.add(org)
    await db_session.commit()
    
    # Retrieve all
    all_orgs = await repo.get_all()
    
    assert len(all_orgs) == 3
    
    names = [org.name for org in all_orgs]
    assert "Org 1" in names
    assert "Org 2" in names
    assert "Org 3" in names


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_empty_database(db_session):
    """Test retrieving all organizations when none exist."""
    repo = OrganizationRepo(db_session)
    
    all_orgs = await repo.get_all()
    
    assert isinstance(all_orgs, list)
    assert len(all_orgs) == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_update_organization(db_session):
    """Test updating an organization."""
    repo = OrganizationRepo(db_session)
    
    # Create and add organization
    organization = Organization(
        name="Original Name",
        description="Original description"
    )
    saved_org = await repo.add(organization)
    await db_session.commit()
    
    # Update the organization
    saved_org.name = "Updated Name"
    saved_org.description = "Updated description"
    updated_org = await repo.update(saved_org)
    await db_session.commit()
    
    # Verify update
    retrieved = await repo.get_by_id(saved_org.id)
    assert retrieved.name == "Updated Name"
    assert retrieved.description == "Updated description"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_organization(db_session):
    """Test deleting an organization."""
    repo = OrganizationRepo(db_session)
    
    # Create and add organization
    organization = Organization(
        name="To Be Deleted",
        description="This will be deleted"
    )
    saved_org = await repo.add(organization)
    await db_session.commit()
    
    org_id = saved_org.id
    
    # Verify it exists
    existing = await repo.get_by_id(org_id)
    assert existing is not None
    
    # Delete it
    await repo.delete(saved_org)
    await db_session.commit()
    
    # Verify it's gone
    deleted = await repo.get_by_id(org_id)
    assert deleted is None


@pytest.mark.asyncio(loop_scope="session")
async def test_organization_with_null_description(db_session):
    """Test creating and retrieving organization with null description."""
    repo = OrganizationRepo(db_session)
    
    organization = Organization(name="No Description Org")
    saved_org = await repo.add(organization)
    await db_session.commit()
    
    retrieved = await repo.get_by_id(saved_org.id)
    assert retrieved.name == "No Description Org"
    assert retrieved.description is None


@pytest.mark.asyncio(loop_scope="session")
async def test_organization_with_empty_description(db_session):
    """Test creating and retrieving organization with empty description."""
    repo = OrganizationRepo(db_session)
    
    organization = Organization(
        name="Empty Description Org",
        description=""
    )
    saved_org = await repo.add(organization)
    await db_session.commit()
    
    retrieved = await repo.get_by_id(saved_org.id)
    assert retrieved.name == "Empty Description Org"
    assert retrieved.description == ""


@pytest.mark.asyncio(loop_scope="session")
async def test_multiple_organizations_same_description(db_session):
    """Test that multiple organizations can have the same description."""
    repo = OrganizationRepo(db_session)
    
    org1 = Organization(name="Org 1", description="Same description")
    org2 = Organization(name="Org 2", description="Same description")
    
    await repo.add(org1)
    await repo.add(org2)
    await db_session.commit()
    
    all_orgs = await repo.get_all()
    assert len(all_orgs) == 2
    
    descriptions = [org.description for org in all_orgs]
    assert descriptions.count("Same description") == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_organization_name_whitespace_handling(db_session):
    """Test organization names with whitespace are preserved."""
    repo = OrganizationRepo(db_session)
    
    # Test with leading/trailing spaces
    org_with_spaces = Organization(name="  Spaced Org  ")
    saved_org = await repo.add(org_with_spaces)
    await db_session.commit()
    
    # Retrieve and verify spaces are preserved
    retrieved = await repo.get_by_name("  Spaced Org  ")
    assert retrieved is not None
    assert retrieved.name == "  Spaced Org  "
    
    # Verify exact match is required
    no_spaces = await repo.get_by_name("Spaced Org")
    assert no_spaces is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_name_with_special_characters(db_session):
    """Test retrieving organization with special characters in name."""
    repo = OrganizationRepo(db_session)
    
    special_names = [
        "Org & Co.",
        "Org-With-Hyphens",
        "Org_With_Underscores",
        "Org (Parentheses)",
        "Org's Apostrophe",
        "Org@Email.com"
    ]
    
    # Create organizations with special characters
    for name in special_names:
        org = Organization(name=name)
        await repo.add(org)
    await db_session.commit()
    
    # Verify each can be retrieved
    for name in special_names:
        retrieved = await repo.get_by_name(name)
        assert retrieved is not None
        assert retrieved.name == name


@pytest.mark.asyncio(loop_scope="session")
async def test_concurrent_operations(db_session):
    """Test that basic repository operations work with async context."""
    repo = OrganizationRepo(db_session)
    
    # Create organization
    org = Organization(name="Concurrent Test Org")
    saved_org = await repo.add(org)
    await db_session.commit()
    
    # Perform multiple operations
    retrieved_by_id = await repo.get_by_id(saved_org.id)
    retrieved_by_name = await repo.get_by_name("Concurrent Test Org")
    all_orgs = await repo.get_all()
    
    # Verify all operations succeeded
    assert retrieved_by_id is not None
    assert retrieved_by_name is not None
    assert len(all_orgs) >= 1
    assert any(org.name == "Concurrent Test Org" for org in all_orgs)