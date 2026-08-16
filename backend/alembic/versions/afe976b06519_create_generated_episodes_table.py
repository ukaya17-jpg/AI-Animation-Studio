"""create generated_episodes table"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "afe976b06519"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "generated_episodes",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("theme_id", sa.Text(), nullable=False),
        sa.Column("theme_label", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("lead_character_id", sa.Text(), nullable=False),
        sa.Column("support_character_id", sa.Text(), nullable=False),
        sa.Column("location_id", sa.Text(), nullable=False),
        sa.Column("lesson", sa.Text(), nullable=False),
        sa.Column("scenes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("seo_package", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("shorts_plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_generated_episodes_created_at", "generated_episodes", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_generated_episodes_created_at", table_name="generated_episodes")
    op.drop_table("generated_episodes")
