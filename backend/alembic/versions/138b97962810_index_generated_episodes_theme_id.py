"""add index on generated_episodes.theme_id"""

from alembic import op

revision = "138b97962810"
down_revision = "5d693758d125"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_generated_episodes_theme_id", "generated_episodes", ["theme_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_generated_episodes_theme_id", table_name="generated_episodes")
