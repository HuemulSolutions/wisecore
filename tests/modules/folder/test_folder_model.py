from uuid import uuid4

from src.modules.folder.models import Folder


def test_folder_full_path_and_root_flag():
    organization_id = uuid4()
    root = Folder(name="root", organization_id=organization_id)
    root.id = uuid4()

    child = Folder(
        name="child",
        organization_id=organization_id,
        parent_folder=root,
    )
    child.parent_folder_id = root.id

    assert root.full_path == "root"
    assert child.full_path == "root/child"
    assert root.is_root is True
    assert child.is_root is False
