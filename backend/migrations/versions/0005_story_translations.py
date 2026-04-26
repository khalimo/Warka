"""add story translations"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0005_story_translations"
down_revision = "0004_ai_review_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")
    with op.batch_alter_table("stories") as batch_op:
        batch_op.add_column(sa.Column("translations", json_type, nullable=False, server_default=sa.text("'{}'")))


def downgrade() -> None:
    with op.batch_alter_table("stories") as batch_op:
        batch_op.drop_column("translations")
