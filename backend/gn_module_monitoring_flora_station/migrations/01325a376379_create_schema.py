"""create schema

Revision ID: 01325a376379
Revises:
Create Date: 2026-07-20 13:01:22.179298

"""

from importlib.resources import read_text

from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "01325a376379"
down_revision = None
branch_labels = "monitoring_flora_station"
depends_on = None


def upgrade():
    operations = text(
        read_text("gn_module_monitoring_flora_station.migrations.data", "schema.sql")
    )
    op.get_bind().execute(operations)


def downgrade():
    op.execute("DROP SCHEMA pr_monitoring_flora_station CASCADE")