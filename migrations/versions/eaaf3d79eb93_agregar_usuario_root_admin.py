"""agregar usuario root admin

Revision ID: eaaf3d79eb93
Revises: a4f070881b45
Create Date: 2025-12-03 07:47:32.288146

"""
from typing import Sequence, Union
import os
from datetime import datetime, timezone
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = 'eaaf3d79eb93'
down_revision: Union[str, Sequence[str], None] = 'a4f070881b45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Obtener email del admin de las variables de entorno
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        raise ValueError("ADMIN_EMAIL environment variable is required but not set")
    
    # Crear referencias a las tablas
    users = table('users',
        column('id', sa.UUID),
        column('email', sa.String),
        column('name', sa.String),
        column('last_name', sa.String),
        column('is_root_admin', sa.Boolean),
        column('status', sa.String),
        column('activated_at', sa.DateTime),
        column('auth_type_id', sa.UUID),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )
    
    connection = op.get_bind()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Obtener el tipo de autenticación INTERNAL
    internal_auth_type = connection.execute(
        sa.text("SELECT id FROM auth_types WHERE type = 'INTERNAL'")
    ).fetchone()
    
    if not internal_auth_type:
        raise ValueError("No se encontró el tipo de autenticación INTERNAL en la base de datos")
    
    auth_type_id = internal_auth_type[0]
    
    # Verificar si el usuario admin ya existe
    existing_user = connection.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": admin_email}
    ).fetchone()
    
    if not existing_user:
        # Crear el usuario root admin
        connection.execute(
            users.insert().values(
                id=uuid.uuid4(),
                email=admin_email,
                name='Root',
                last_name='Admin',
                is_root_admin=True,
                status='active',
                activated_at=now,
                auth_type_id=auth_type_id,
                created_at=now,
                updated_at=now
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        connection = op.get_bind()
        # Eliminar el usuario admin
        connection.execute(
            sa.text("DELETE FROM users WHERE email = :email AND is_root_admin = true"),
            {"email": admin_email}
        )
