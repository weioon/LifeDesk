"""Create persistent tasks."""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_tasks"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.String(6), server_default="medium", nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("length(trim(title)) BETWEEN 1 AND 200", name="ck_tasks_title"),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high')", name="ck_tasks_priority"),
        sa.CheckConstraint("is_completed IN (0, 1)", name="ck_tasks_is_completed"),
        sa.CheckConstraint(
            "(is_completed = 0 AND completed_at IS NULL) OR "
            "(is_completed = 1 AND completed_at IS NOT NULL)",
            name="ck_tasks_completion",
        ),
    )


def downgrade():
    op.drop_table("tasks")
