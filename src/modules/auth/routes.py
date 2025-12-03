from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session

from src.database.core import get_session
from src.schemas import ResponseSchema
from src.utils import get_transaction_id
from .models import CodePurpose
from .schemas import CreateUser, RequestCode, VerifyCode
from .service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/users")
async def create_user(
    request: CreateUser,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    auth_service = AuthService(session)
    try:
        user, token = await auth_service.create_user(
            request.name,
            request.last_name,
            request.email,
            request.code,
        )
        return ResponseSchema(
            transaction_id=transaction_id,
            data={"user": jsonable_encoder(user), "token": token},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"Ocurrió un error al crear el usuario: {str(exc)}",
            },
        )


@router.post("/codes")
async def generate_login_code(
    request: RequestCode,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    auth_service = AuthService(session)
    try:
        if request.purpose == CodePurpose.SIGNUP:
            code = await auth_service.generate_signup_code(request.email)
            message = "Código de registro generado y enviado."
        else:
            code = await auth_service.generate_login_code(request.email)
            message = "Código de acceso generado y enviado."
        return ResponseSchema(
            transaction_id=transaction_id,
            data={
                "message": message,
                "expires_at": code.expires_at,
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"Ocurrió un error al generar el código: {str(exc)}",
            },
        )


@router.post("/codes/verify")
async def verify_login_code(
    request: VerifyCode,
    session: Session = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    auth_service = AuthService(session)
    try:
        user, token = await auth_service.verify_login_code(request.email, request.code)
        return ResponseSchema(
            transaction_id=transaction_id,
            data={
                "message": "Código verificado correctamente.",
                "user": jsonable_encoder(user),
                "token": token,
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "transaction_id": transaction_id,
                "error": f"Ocurrió un error al verificar el código: {str(exc)}",
            },
        )
