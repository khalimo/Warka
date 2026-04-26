"""add cluster event metadata"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006_cluster_event_metadata"
down_revision = "0005_story_translations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")
    with op.batch_alter_table("clusters") as batch_op:
        batch_op.add_column(sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("event_signature", json_type, nullable=False, server_default=sa.text("'{}'")))


def downgrade() -> None:
    with op.batch_alter_table("clusters") as batch_op:
        batch_op.drop_column("event_signature")
        batch_op.drop_column("confidence_score")
