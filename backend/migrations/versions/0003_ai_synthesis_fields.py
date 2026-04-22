"""add ai synthesis fields to clusters"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_ai_synthesis_fields"
down_revision = "0002_source_registry_health"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("clusters") as batch_op:
        batch_op.add_column(sa.Column("ai_neutral_summary", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("ai_coverage_differences", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("ai_consensus_level", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("ai_key_themes", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("ai_generated_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("ai_model_used", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("has_ai_synthesis", sa.Boolean(), nullable=False, server_default=sa.text("0"))
        )


def downgrade() -> None:
    with op.batch_alter_table("clusters") as batch_op:
        batch_op.drop_column("has_ai_synthesis")
        batch_op.drop_column("ai_model_used")
        batch_op.drop_column("ai_generated_at")
        batch_op.drop_column("ai_key_themes")
        batch_op.drop_column("ai_consensus_level")
        batch_op.drop_column("ai_coverage_differences")
        batch_op.drop_column("ai_neutral_summary")
