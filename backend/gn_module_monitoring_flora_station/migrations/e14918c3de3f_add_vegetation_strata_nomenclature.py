"""add vegetation strata nomenclature

Revision ID: e14918c3de3f
Revises: 5e202272f668
Create Date: 2026-08-19 00:00:00.000000

"""

from importlib.resources import open_text

from gn_conservation_backend_shared.migrations.utils import csv, nomenclatures
from utils_flask_sqla.migrations.utils import logger


# revision identifiers, used by Alembic.
revision = "e14918c3de3f"
down_revision = "5e202272f668"
branch_labels = None
depends_on = None


def upgrade():
    nomenclatures.add_nomenclature_type(
            mnemonic="STRATE_VEGETATION_MFS",
            label="Strates de végétation",
            definition="Nomenclature des strates de végétation pour placette (module Suivi Flore Station).",
            source="CBNA",
    )

    with open_text(
        "gn_module_monitoring_flora_station.migrations.data", "nomenclatures_strate_vegetation.csv"
    ) as csvfile:
        logger.info("Inserting vegetation strata nomenclature…")
        csv.copy_from_csv(
            csvfile,
            schema="ref_nomenclatures",
            table="t_nomenclatures",
            dest_cols=(
                "id_type",
                "cd_nomenclature",
                "mnemonique",
                "label_default",
                "definition_default",
                "label_fr",
                "definition_fr",
                "id_broader",
                "hierarchy",
            ),  # type: ignore
            source_cols=(
                "ref_nomenclatures.get_id_nomenclature_type(type_nomenclature_code)",
                "cd_nomenclature",
                "mnemonique",
                "label_default",
                "definition_default",
                "label_fr",
                "definition_fr",
                "ref_nomenclatures.get_id_nomenclature(type_nomenclature_code, cd_nomenclature_broader)",
                "hierarchy",
            ),
            header=True,
            encoding="UTF-8",
            delimiter=",",
        )


def downgrade():
    nomenclatures.delete_nomenclatures_by_type("STRATE_VEGETATION_MFS")