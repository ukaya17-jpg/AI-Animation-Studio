"""add nullable project_id to generated_episodes"""

import sqlalchemy as sa

from alembic import op

revision = "5d693758d125"
down_revision = "2d5160e78e57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generated_episodes",
        sa.Column("project_id", sa.Uuid(as_uuid=True), sa.ForeignKey("projects.id"), nullable=True),
    )
    op.create_index(
        "ix_generated_episodes_project_id", "generated_episodes", ["project_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_generated_episodes_project_id", table_name="generated_episodes")
    op.drop_column("generated_episodes", "project_id")
