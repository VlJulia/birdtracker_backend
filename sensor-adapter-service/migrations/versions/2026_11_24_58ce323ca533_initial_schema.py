"""initial schema"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "58ce323ca533"
down_revision = None


def upgrade() -> None:
    # if_not_exists: в уже работающей базе эту таблицу создал create_all
    op.create_table(
        "sensor_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=24), nullable=False),
        sa.Column("timestamp", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    for column in ("id", "device_id", "timestamp"):
        op.create_index(
            f"ix_sensor_messages_{column}",
            "sensor_messages",
            [column],
            if_not_exists=True,
        )


def downgrade() -> None:
    op.drop_table("sensor_messages")
