import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_list_organizations(client):
    """Test successful creation and listing of organizations."""
    create_response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Integration Org", "description": "Created from tests"},
    )

    assert create_response.status_code == 200
    created_payload = create_response.json()
    created_org = created_payload["data"]

    assert created_org["name"] == "Integration Org"
    assert created_org["description"] == "Created from tests"
    assert "transaction_id" in created_payload

    list_response = await client.get("/api/v1/organizations/")
    assert list_response.status_code == 200

    list_payload = list_response.json()
    organizations = list_payload["data"]

    assert isinstance(organizations, list)
    assert len(organizations) == 1
    assert organizations[0]["name"] == "Integration Org"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_without_description(client):
    """Test creating organization without description (optional field)."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Org Without Description"},
    )

    assert response.status_code == 200
    payload = response.json()
    org_data = payload["data"]

    assert org_data["name"] == "Org Without Description"
    assert "transaction_id" in payload
    # Description should be None or not present
    assert org_data.get("description") is None or "description" not in org_data


@pytest.mark.asyncio(loop_scope="session") 
async def test_create_organization_with_empty_description(client):
    """Test creating organization with empty description."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Org With Empty Description", "description": ""},
    )

    assert response.status_code == 200
    payload = response.json()
    org_data = payload["data"]

    assert org_data["name"] == "Org With Empty Description"
    assert org_data["description"] == ""
    assert "transaction_id" in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_missing_name(client):
    """Test creating organization without required name field."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"description": "Org without name"},
    )

    assert response.status_code == 422  # Validation error
    payload = response.json()
    assert "detail" in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_empty_name(client):
    """Test creating organization with empty name."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"name": "", "description": "Empty name org"},
    )

    # This should either be a 400 (business logic error) or 422 (validation error)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_invalid_json(client):
    """Test creating organization with invalid JSON payload."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"name": 123, "description": ["invalid", "type"]},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio(loop_scope="session")
async def test_get_organizations_empty_list(client):
    """Test getting organizations when no organizations exist."""
    # First ensure we start with empty state
    list_response = await client.get("/api/v1/organizations/")
    
    assert list_response.status_code == 200
    payload = list_response.json()
    organizations = payload["data"]
    
    assert isinstance(organizations, list)
    assert "transaction_id" in payload


@pytest.mark.asyncio(loop_scope="session")
async def test_multiple_organizations_creation_and_listing(client):
    """Test creating multiple organizations and listing them."""
    organizations_data = [
        {"name": "Tech Corp", "description": "Technology company"},
        {"name": "Finance Inc", "description": "Financial services"},
        {"name": "Health Ltd"},  # Without description
    ]
    
    created_orgs = []
    
    # Create multiple organizations
    for org_data in organizations_data:
        response = await client.post("/api/v1/organizations/", json=org_data)
        assert response.status_code == 200
        
        payload = response.json()
        created_org = payload["data"]
        created_orgs.append(created_org)
        
        assert created_org["name"] == org_data["name"]
        if "description" in org_data:
            assert created_org["description"] == org_data["description"]
        assert "transaction_id" in payload
    
    # List all organizations
    list_response = await client.get("/api/v1/organizations/")
    assert list_response.status_code == 200
    
    list_payload = list_response.json()
    organizations = list_payload["data"]
    
    assert isinstance(organizations, list)
    assert len(organizations) >= 3  # At least the 3 we just created
    assert "transaction_id" in list_payload
    
    # Verify all created organizations are in the list
    org_names = [org["name"] for org in organizations]
    for org_data in organizations_data:
        assert org_data["name"] in org_names


@pytest.mark.asyncio(loop_scope="session")
async def test_create_organization_response_structure(client):
    """Test that organization creation response has correct structure."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Structure Test Org", "description": "Testing response structure"},
    )

    assert response.status_code == 200
    payload = response.json()
    
    # Check response structure
    assert "transaction_id" in payload
    assert "data" in payload
    assert isinstance(payload["transaction_id"], str)
    
    org_data = payload["data"]
    assert isinstance(org_data, dict)
    assert "name" in org_data
    assert "description" in org_data
    # Should also have ID and timestamps if included in the model
    

@pytest.mark.asyncio(loop_scope="session") 
async def test_get_organizations_response_structure(client):
    """Test that get organizations response has correct structure."""
    response = await client.get("/api/v1/organizations/")
    
    assert response.status_code == 200
    payload = response.json()
    
    # Check response structure
    assert "transaction_id" in payload
    assert "data" in payload
    assert isinstance(payload["transaction_id"], str)
    assert isinstance(payload["data"], list)
