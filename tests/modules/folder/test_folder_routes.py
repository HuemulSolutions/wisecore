import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.main import app
from src.database.core import get_session
from src.modules.document.models import Document
from src.modules.document_type.models import DocumentType
from src.modules.folder.models import Folder
from src.modules.organization.models import Organization
from src.utils import get_transaction_id


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_session():
        yield db_session

    def override_get_transaction_id():
        return "test-transaction-id"

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_transaction_id] = override_get_transaction_id

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.pop(get_session, None)
    app.dependency_overrides.pop(get_transaction_id, None)


@pytest.mark.asyncio
async def test_create_folder_route_creates_folder(client, db_session):
    org = Organization(name="Acme", description=None)
    db_session.add(org)
    await db_session.flush()

    payload = {"name": "Projects", "organization_id": str(org.id)}

    response = await client.post("/api/v1/folder/create_folder", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["transaction_id"] == "test-transaction-id"

    data = body["data"]
    assert data["name"] == "Projects"
    assert data["organization_id"] == str(org.id)
    assert data["parent_folder_id"] is None

    stored = await db_session.get(Folder, data["id"])
    assert stored is not None
    assert stored.name == "Projects"


@pytest.mark.asyncio
async def test_get_folder_content_route_returns_root_items(client, db_session):
    org = Organization(name="Wise", description=None)
    db_session.add(org)
    await db_session.flush()

    folder = Folder(name="Root folder", organization_id=org.id)
    db_session.add(folder)

    doc_type = DocumentType(name="Manual", color="#FFFFFF", organization_id=org.id)
    db_session.add(doc_type)
    await db_session.flush()

    document = Document(
        name="Project Plan",
        description="Initial plan",
        organization_id=org.id,
        document_type_id=doc_type.id,
        folder_id=None,
    )
    db_session.add(document)
    await db_session.flush()

    response = await client.get(
        "/api/v1/folder/root",
        headers={"OrganizationId": str(org.id)},
    )
    assert response.status_code == 200

    payload = response.json()
    content = payload["data"]["content"]

    folder_entry = next(item for item in content if item["type"] == "folder")
    assert folder_entry["id"] == str(folder.id)
    assert folder_entry["name"] == "Root folder"

    document_entry = next(item for item in content if item["type"] == "document")
    assert document_entry["id"] == str(document.id)
    assert document_entry["document_type"]["name"] == "Manual"


@pytest.mark.asyncio
async def test_delete_folder_route_removes_folder(client, db_session):
    org = Organization(name="Umbrella", description=None)
    db_session.add(org)
    await db_session.flush()

    folder = Folder(name="Obsolete", organization_id=org.id)
    db_session.add(folder)
    await db_session.flush()

    response = await client.delete(f"/api/v1/folder/{folder.id}")
    assert response.status_code == 200
    body = response.json()

    assert body["transaction_id"] == "test-transaction-id"
    assert body["data"]["folder_id"] == str(folder.id)

    deleted = await db_session.get(Folder, folder.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_folder_route_returns_not_found_for_unknown_folder(client):
    missing_id = uuid.uuid4()

    response = await client.delete(f"/api/v1/folder/{missing_id}")
    assert response.status_code == 404

    body = response.json()
    assert body["transaction_id"] == "test-transaction-id"
    assert "not found" in body["error"].lower()
