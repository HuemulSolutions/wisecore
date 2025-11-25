import asyncio
from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.mail import BaseMailProvider, get_provider
from .models import CodePurpose, LoginCode, User
from .repository import LoginCodeRepo, UserRepo
from src.utils import generate_jwt_token


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        mail_provider: Optional[BaseMailProvider] = None,
    ):
        self.session = session
        self.user_repo = UserRepo(session)
        self.login_code_repo = LoginCodeRepo(session)
        self.mail_provider = mail_provider or get_provider()

    async def create_user(self, username: str, email: str, code: str) -> Tuple[User, str]:
        """
        Create a new user after validating a sign-up code.
        """
        sanitized_username = username.strip() if username else ""
        sanitized_email = email.strip().lower() if email else ""
        sanitized_code = code.strip() if code else ""

        if not sanitized_username:
            raise ValueError("El nombre de usuario es obligatorio.")
        if not sanitized_email:
            raise ValueError("El email es obligatorio.")
        if not sanitized_code:
            raise ValueError("El código de verificación es obligatorio.")

        if await self.user_repo.get_by_email(sanitized_email):
            raise ValueError("Ya existe un usuario con ese email.")

        if await self.user_repo.get_by_username(sanitized_username):
            raise ValueError("Ya existe un usuario con ese nombre de usuario.")

        # Validate and consume sign-up code
        signup_code = await self._verify_and_consume_code(
            sanitized_email, sanitized_code, CodePurpose.SIGNUP
        )

        user = User(username=sanitized_username, email=sanitized_email)
        user = await self.user_repo.add(user)

        # Link the code to the newly created user for traceability
        if signup_code.user_id is None:
            signup_code.user_id = user.id
            await self.login_code_repo.update(signup_code)

        token = generate_jwt_token({"sub": str(user.id), "email": user.email})
        return user, token

    async def get_user_by_email(self, email: str) -> User:
        """
        Retrieve a user by email or raise if it does not exist.
        """
        sanitized_email = email.strip().lower() if email else ""
        if not sanitized_email:
            raise ValueError("El email es obligatorio.")

        user = await self.user_repo.get_by_email(sanitized_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        return user

    async def generate_signup_code(self, email: str) -> LoginCode:
        """
        Create a sign-up code for a new user and send it via email.
        """
        sanitized_email = email.strip().lower() if email else ""
        if not sanitized_email:
            raise ValueError("El email es obligatorio.")
        if await self.user_repo.get_by_email(sanitized_email):
            raise ValueError("Ya existe un usuario con ese email.")

        code = self._generate_six_digit_code()
        login_code = LoginCode(
            email=sanitized_email,
            purpose=CodePurpose.SIGNUP.value,
            code=code,
            user_id=None,
            expires_at=self._get_expiry_time(),
        )
        login_code = await self.login_code_repo.add(login_code)

        sent = await asyncio.to_thread(
            self.mail_provider.send_verification_code,
            sanitized_email,
            code,
        )
        if not sent:
            raise Exception("No se pudo enviar el código de verificación por correo.")

        return login_code

    async def generate_login_code(self, email: str) -> LoginCode:
        """
        Create a new 6-digit login code for the user and send it via email.
        """
        user = await self.get_user_by_email(email)
        code = self._generate_six_digit_code()

        login_code = LoginCode(
            user_id=user.id,
            email=user.email,
            purpose=CodePurpose.LOGIN.value,
            code=code,
            expires_at=self._get_expiry_time(),
        )
        login_code = await self.login_code_repo.add(login_code)

        sent = await asyncio.to_thread(
            self.mail_provider.send_verification_code,
            user.email,
            code,
        )
        if not sent:
            raise Exception("No se pudo enviar el código de verificación por correo.")

        return login_code

    async def verify_login_code(self, email: str, code: str) -> Tuple[User, str]:
        """
        Verify and consume a login code for an existing user.
        """
        user = await self.get_user_by_email(email)
        await self._verify_and_consume_code(
            user.email, code, CodePurpose.LOGIN, user.id
        )
        token = generate_jwt_token({"sub": str(user.id), "email": user.email})
        return user, token

    async def _verify_and_consume_code(
        self,
        email: str,
        code: str,
        purpose: CodePurpose,
        user_id: Optional[str] = None,
    ) -> LoginCode:
        """
        Validate the latest code for the email/purpose and mark it as used.
        """
        sanitized_email = email.strip().lower() if email else ""
        sanitized_code = code.strip() if code else ""
        if not sanitized_email:
            raise ValueError("El email es obligatorio.")
        if not sanitized_code:
            raise ValueError("El código es obligatorio.")

        login_code = await self.login_code_repo.get_latest(
            sanitized_email, purpose, user_id
        )

        if not login_code:
            raise ValueError("No hay códigos generados para este propósito.")

        if login_code.is_used:
            raise ValueError("El código ya fue utilizado.")

        if login_code.is_expired():
            raise ValueError("El código ha expirado.")

        if login_code.attempts >= 3:
            raise ValueError("Se superó el número máximo de intentos.")

        if login_code.code != sanitized_code:
            login_code.attempts += 1
            await self.login_code_repo.update(login_code)
            raise ValueError("Código incorrecto.")

        login_code.is_used = True
        if user_id and not login_code.user_id:
            login_code.user_id = user_id
        await self.login_code_repo.update(login_code)
        return login_code

    def _generate_six_digit_code(self) -> str:
        """Generate a zero-padded 6-digit code."""
        return f"{secrets.randbelow(1_000_000):06d}"

    def _get_expiry_time(self) -> datetime:
        """Return a timezone-naive expiry timestamp (15 minutes from now)."""
        return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
