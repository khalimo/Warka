"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")

    op.create_table(
        "sources",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=True),
        sa.Column("feed_url", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(), nullable=False, server_default="so"),
        sa.Column("country", sa.String(), nullable=False, server_default="SO"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "clusters",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("common_facts", sa.Text(), nullable=True),
        sa.Column("coverage_differences", sa.Text(), nullable=True),
        sa.Column("neutral_summary", sa.Text(), nullable=True),
        sa.Column("key_themes", json_type, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("consensus_level", sa.String(), nullable=True),
        sa.Column("story_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "ingest_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("processed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("details_json", json_type, nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_ingest_runs_status", "ingest_runs", ["status"])

    op.create_table(
        "stories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("content_html", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_id", sa.String(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("original_url", sa.String(), nullable=False),
        sa.Column("canonical_url_hash", sa.String(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("topics", json_type, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("reading_time", sa.Integer(), nullable=True),
        sa.Column("is_breaking", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("cluster_id", sa.String(), sa.ForeignKey("clusters.id"), nullable=True),
        sa.Column("framing_label", sa.String(), nullable=True),
        sa.Column("framing_description", sa.Text(), nullable=True),
        sa.Column("framing_tone", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_stories_slug", "stories", ["slug"], unique=True)
    op.create_index("ix_stories_canonical_url_hash", "stories", ["canonical_url_hash"], unique=True)
    op.create_index("ix_stories_published_at", "stories", ["published_at"])
    op.create_index("ix_stories_region", "stories", ["region"])
    op.create_index("ix_stories_category", "stories", ["category"])
    op.create_index("ix_stories_cluster_id", "stories", ["cluster_id"])
    op.create_index("ix_stories_source_id", "stories", ["source_id"])


def downgrade() -> None:
    op.drop_index("ix_stories_source_id", table_name="stories")
    op.drop_index("ix_stories_cluster_id", table_name="stories")
    op.drop_index("ix_stories_category", table_name="stories")
    op.drop_index("ix_stories_region", table_name="stories")
    op.drop_index("ix_stories_published_at", table_name="stories")
    op.drop_index("ix_stories_canonical_url_hash", table_name="stories")
    op.drop_index("ix_stories_slug", table_name="stories")
    op.drop_table("stories")
    op.drop_index("ix_ingest_runs_status", table_name="ingest_runs")
    op.drop_table("ingest_runs")
    op.drop_table("clusters")
    op.drop_table("sources")
