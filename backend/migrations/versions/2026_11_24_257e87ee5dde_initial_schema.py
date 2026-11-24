"""initial schema"""

import sqlalchemy as sa
from alembic import op

revision = "257e87ee5dde"
down_revision = None


def upgrade() -> None:
    # if_not_exists: в уже работающей базе эти таблицы создал create_all
    op.create_table(
        "birds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bird_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bird_name"),
        if_not_exists=True,
    )
    op.create_index("ix_birds_id", "birds", ["id"], if_not_exists=True)

    op.create_table(
        "sensor_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index(
        "ix_sensor_versions_id", "sensor_versions", ["id"], if_not_exists=True
    )
    op.create_index(
        "ix_sensor_versions_version",
        "sensor_versions",
        ["version"],
        unique=True,
        if_not_exists=True,
    )

    op.create_table(
        "sensors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("internal_id", sa.String(), nullable=True),
        sa.Column("version_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["version_id"], ["sensor_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index("ix_sensors_id", "sensors", ["id"], if_not_exists=True)
    op.create_index(
        "ix_sensors_internal_id",
        "sensors",
        ["internal_id"],
        unique=True,
        if_not_exists=True,
    )

    op.create_table(
        "sensor_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("is_light", sa.Boolean(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("sensor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.id"]),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index("ix_sensor_data_id", "sensor_data", ["id"], if_not_exists=True)


def downgrade() -> None:
    op.drop_table("sensor_data")
    op.drop_table("sensors")
    op.drop_table("sensor_versions")
    op.drop_table("birds")
