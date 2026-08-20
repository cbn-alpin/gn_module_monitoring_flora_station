"""clean substrate nomenclature labels

Revision ID: 60d04a225399
Revises: e14918c3de3f
Create Date: 2026-08-19 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "60d04a225399"
down_revision = "e14918c3de3f"
branch_labels = None
depends_on = None


SUBSTRATE_LABELS = {
    "Rec": ("Eau circulante", "Eau circulante"),
    "Res": ("Eau stagnante", "Eau stagnante"),
    "Rsn": ("Sol nu", "Sol nu"),
    "Rro": ("Rochers", "Rochers"),
    "Rbl": ("Blocs", "Blocs > 20 cm"),
    "Rca": ("Cailloux", "Cailloux 2-20 cm"),
    "Rgr": ("Graviers", "Graviers 2mm-2cm"),
    "Rsf": ("Sédiments fins", "Sédiments fins < 2mm"),
    "Rsa": ("Substrat artificiel", "Substrat artificiel"),
    "Rlh": ("Litière - Humus", "Litière - Humus"),
    "Rto": ("Tourbe", "Tourbe"),
    "Rtu": ("Tuf", "Tuf"),
}

OLD_SUBSTRATE_LABELS = {
    "Rec": ("Recouvrement eau circulante", "Recouvrement eau circulante"),
    "Res": ("Recouvrement eau stagnante", "Recouvrement eau stagnante"),
    "Rsn": ("Recouvrement sol nu", "Recouvrement sol nu"),
    "Rro": ("Recouvrement rochers", "Recouvrement rochers"),
    "Rbl": ("Recouvrement blocs", "Recouvrement blocs > 20 cm"),
    "Rca": ("Recouvrement cailloux", "Recouvrement cailloux 2-20 cm"),
    "Rgr": ("Recouvrement graviers", "Recouvrement graviers 2mm-2cm"),
    "Rsf": ("Recouvrement sédiments fins", "Recouvrement sédiments fins < 2mm"),
    "Rsa": ("Recouvrement substrat artificiel", "Recouvrement substrat artificiel"),
    "Rlh": ("Recouvrement litière-humus", "Recouvrement litière-humus"),
    "Rto": ("Recouvrement tourbe", "Recouvrement tourbe"),
    "Rtu": ("Recouvrement tuf", "Recouvrement tuf"),
}


def _apply_labels(labels):
    for cd_nomenclature, (label, definition) in labels.items():
        op.execute(
            f"""
            UPDATE ref_nomenclatures.t_nomenclatures
            SET label_default = '{label}',
                label_fr = '{label}',
                definition_default = '{definition}',
                definition_fr = '{definition}'
            WHERE cd_nomenclature = '{cd_nomenclature}'
              AND id_type = (
                  SELECT id_type FROM ref_nomenclatures.bib_nomenclatures_types
                  WHERE mnemonique = 'SUBSTRAT_PLACETTE'
              )
            """
        )


def upgrade():
    _apply_labels(SUBSTRATE_LABELS)


def downgrade():
    _apply_labels(OLD_SUBSTRATE_LABELS)