"""update module label and description

Revision ID: 5e202272f668
Revises: 880bfa0763c4
Create Date: 2026-08-19 00:00:00.000000

"""

from gn_conservation_backend_shared.migrations.utils import commons

from gn_module_monitoring_flora_station import MODULE_CODE


# revision identifiers, used by Alembic.
revision = "5e202272f668"
down_revision = "880bfa0763c4"
branch_labels = None
depends_on = None


def upgrade():
    commons.update_module(
        code=MODULE_CODE,
        label="Suivi Flore Station",
        description="Module de suivi de stations de flore.",
        doc_url="https://github.com/cbn-alpin/gn_module_monitoring_flora_station/",
    )


def downgrade():
    pass