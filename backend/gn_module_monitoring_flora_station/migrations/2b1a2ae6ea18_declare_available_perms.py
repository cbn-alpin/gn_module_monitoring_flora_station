"""declare available perms

Revision ID: <garder celui généré>
Revises: 01325a376379
Create Date: ...

"""

from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "2b1a2ae6ea18"
down_revision = "01325a376379"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        text(
            """
            INSERT INTO gn_permissions.t_permissions_available
                (id_module, id_object, id_action, label, scope_filter, sensitivity_filter)
            SELECT
                m.id_module,
                o.id_object,
                a.id_action,
                label_data.label,
                true,
                false
            FROM gn_commons.t_modules m
            JOIN gn_permissions.t_objects o ON o.code_object = 'ALL'
            JOIN gn_permissions.bib_actions a ON a.code_action IN ('C', 'R', 'U', 'E', 'D')
            JOIN (
                VALUES
                    ('C', 'Ajouter des données au module MFS'),
                    ('R', 'Voir les données du module MFS'),
                    ('U', 'Modifier les données du module MFS'),
                    ('E', 'Exporter les données du module MFS'),
                    ('D', 'Supprimer les données du module MFS')
            ) AS label_data(code_action, label) ON label_data.code_action = a.code_action
            WHERE m.module_code = 'MFS'
            """
        )
    )


def downgrade():
    op.execute(
        text(
            """
            DELETE FROM gn_permissions.t_permissions_available
            WHERE id_module = (SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'MFS')
            """
        )
    )