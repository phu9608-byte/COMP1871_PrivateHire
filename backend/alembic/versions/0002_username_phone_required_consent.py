"""users: add username + marketing_consent, phone required

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-07

Bang users phai TRONG truoc khi chay (username va phone la NOT NULL).
Database tren may: da xoa du lieu. Database Docker: `docker compose down -v` roi build lai.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(30), nullable=False))
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.add_column(
        "users",
        sa.Column("marketing_consent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "phone", existing_type=sa.String(20), nullable=False)


def downgrade() -> None:
    op.alter_column("users", "phone", existing_type=sa.String(20), nullable=True)
    op.drop_column("users", "marketing_consent")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
