import pytest

from src.modules.folder.models import Folder
from src.modules.folder.repository import FolderRepo
from src.modules.organization.models import Organization
from src.modules.document_type.models import DocumentType
from src.modules.document.models import Document


@pytest.mark.asyncio
async def test_get_by_name_respects_both_name_and_parent(db_session):
    org = Organization(name="Acme", description=None)
    db_session.add(org)
    await db_session.flush()

    root = Folder(name="Projects", organization_id=org.id)
    db_session.add(root)

    wrong_child = Folder(name="Archive", organization_id=org.id, parent_folder_id=root.id)
    db_session.add(wrong_child)

    target_child = Folder(name="Projects", organization_id=org.id, parent_folder_id=root.id)
    db_session.add(target_child)
    await db_session.flush()

    repo = FolderRepo(db_session)

    root_lookup = await repo.get_by_name("Projects")
    child_lookup = await repo.get_by_name("Projects", parent_folder_id=root.id)

    assert root_lookup.id == root.id
    assert child_lookup.id == target_child.id


@pytest.mark.asyncio
async def test_get_folder_content_returns_root_items(db_session):
    org = Organization(name="Wise", description=None)
    db_session.add(org)
    await db_session.flush()

    doc_type = DocumentType(name="Report", color="#FFFFFF", organization_id=org.id)
    db_session.add(doc_type)
    await db_session.flush()

    root_folder = Folder(name="Root folder", organization_id=org.id)
    db_session.add(root_folder)

    document = Document(
        name="Project Plan",
        description="Initial plan",
        organization_id=org.id,
        document_type_id=doc_type.id,
        folder_id=None,
    )
    db_session.add(document)
    await db_session.flush()

    repo = FolderRepo(db_session)
    result = await repo.get_folder_content(organization_id=org.id)

    assert result["folder_name"] == "root"
    assert any(item["id"] == str(root_folder.id) and item["type"] == "folder" for item in result["content"])

    document_entry = next(item for item in result["content"] if item["type"] == "document")
    assert document_entry["name"] == "Project Plan"
    assert document_entry["document_type"]["name"] == "Report"
