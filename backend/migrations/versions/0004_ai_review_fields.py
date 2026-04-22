"""add ai review fields to clusters"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_ai_review_fields"
down_revision = "0003_ai_synthesis_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("clusters") as batch_op:
        batch_op.add_column(sa.Column("ai_review_status", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("ai_review_note", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("ai_reviewed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("clusters") as batch_op:
        batch_op.drop_column("ai_reviewed_at")
        batch_op.drop_column("ai_review_note")
        batch_op.drop_column("ai_review_status")
