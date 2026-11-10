"""login lockout columns on users + sessions table

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-07

Khong can xoa du lieu: cot moi co gia tri mac dinh, bang sessions la bang moi.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("users", sa.Column("failed_login_started_at", sa.DateTime(timezone=True)))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True)))

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_started_at")
    op.drop_column("users", "failed_login_count")
