"""add type site nomenclature

Revision ID: 6e4491ebf2f9
Revises: 2b1a2ae6ea18
Create Date: 2026-07-29 11:10:44.667526

"""

from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "6e4491ebf2f9"
down_revision = "2b1a2ae6ea18"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        text(
            """
            INSERT INTO ref_nomenclatures.t_nomenclatures
                (id_type, cd_nomenclature, mnemonique, label_default, label_fr, definition_default, active)
            SELECT
                id_type, 'FLO', 'FLO', 'Zone de suivi flore station', 'Zone de suivi flore station',
                'Type de site pour le module Suivi Flore Station', true
            FROM ref_nomenclatures.bib_nomenclatures_types
            WHERE mnemonique = 'TYPE_SITE'
            AND NOT EXISTS (
                SELECT 1 FROM ref_nomenclatures.t_nomenclatures
                WHERE mnemonique = 'FLO'
                AND id_type = (
                    SELECT id_type FROM ref_nomenclatures.bib_nomenclatures_types
                    WHERE mnemonique = 'TYPE_SITE'
                )
            )
            """
        )
    )


def downgrade():
    op.execute(
        text(
            """
            DELETE FROM ref_nomenclatures.t_nomenclatures
            WHERE mnemonique = 'FLO'
            AND id_type = (
                SELECT id_type FROM ref_nomenclatures.bib_nomenclatures_types
                WHERE mnemonique = 'TYPE_SITE'
            )
            """
        )
    )