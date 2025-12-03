from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session

from src.database.core import get_session
from src.modules.user.service import UserService
from src.modules.user.schemas import UpdateUserInfo
from src.schemas import ResponseSchema
from src.utils import get_current_user, get_transaction_id

router = APIRouter(prefix="/users")


def _require_root_admin(current_user: dict, transaction_id: str):
    if not current_user.get("is_root_admin"):
        raise HTTPException(
            status_code=403,
            detail={
                "transaction_id": transaction_id,
                "error": "Solo un administrador root puede realizar esta acción.",
            },
        )


@router.get("/")
async def list_users(
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
    current_user: dict = Depends(get_current_user),
):
    """
    List all users (root admin only).
    """
    _require_root_admin(current_user, transaction_id)
    service = UserService(session)
    users = await service.list_users()
    return ResponseSchema(
        transaction_id=transaction_id,
        data=jsonable_encoder(users),
    )


@router.post("/{user_id}/approve")
async def approve_user(
    user_id: str,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Approve a pending user (root admin only).
    """
    _require_root_admin(current_user, transaction_id)
    service = UserService(session)
    try:
        user = await service.approve_user(user_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(user),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )


@router.post("/{user_id}/reject")
async def reject_user(
    user_id: str,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Reject a pending user (root admin only).
    """
    _require_root_admin(current_user, transaction_id)
    service = UserService(session)
    try:
        user = await service.reject_user(user_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(user),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a user (root admin only).
    """
    _require_root_admin(current_user, transaction_id)
    service = UserService(session)
    try:
        await service.delete_user(user_id)
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"user_id": user_id},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserInfo,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Update basic user information. Users can update their own profile; root admin can update anyone.
    """
    actor_id = str(current_user.get("sub"))
    is_root_admin = current_user.get("is_root_admin", False)
    if not is_root_admin and actor_id != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "transaction_id": transaction_id,
                "error": "No tienes permisos para actualizar este usuario.",
            },
        )

    service = UserService(session)
    try:
        user = await service.update_user_info(
            user_id=user_id,
            name=request.name,
            last_name=request.last_name,
            birthdate=request.birthdate,
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data=jsonable_encoder(user),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
