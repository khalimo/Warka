"""add source registry and health fields"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_source_registry_health"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sources", sa.Column("source_type", sa.String(), nullable=False, server_default="rss"))
    op.add_column("sources", sa.Column("priority", sa.Integer(), nullable=False, server_default="100"))
    op.add_column("sources", sa.Column("validation_status", sa.String(), nullable=False, server_default="pending"))
    op.add_column("sources", sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sources", sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("sources", sa.Column("avg_response_time_ms", sa.Integer(), nullable=True))
    op.add_column("sources", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("sources", "notes")
    op.drop_column("sources", "avg_response_time_ms")
    op.drop_column("sources", "consecutive_failures")
    op.drop_column("sources", "last_validated_at")
    op.drop_column("sources", "validation_status")
    op.drop_column("sources", "priority")
    op.drop_column("sources", "source_type")
