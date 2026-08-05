"""add export visits view

Revision ID: 880bfa0763c4
Revises: a67a93514c0e
Create Date: 2026-08-04 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "880bfa0763c4"
down_revision = "a67a93514c0e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE VIEW pr_monitoring_flora_station.export_visits AS
        WITH observers AS (
            SELECT
                v.id_base_visit,
                string_agg(
                    DISTINCT (
                        roles.prenom_role || ' ' || roles.nom_role || ' (' || bo.nom_organisme || ')'
                    ),
                    ', '
                ) AS observers
            FROM gn_monitoring.t_base_visits AS v
                JOIN gn_monitoring.cor_visit_observer AS observer
                    ON observer.id_base_visit = v.id_base_visit
                JOIN utilisateurs.t_roles AS roles
                    ON roles.id_role = observer.id_role
                JOIN utilisateurs.bib_organismes AS bo
                    ON bo.id_organisme = roles.id_organisme
            GROUP BY v.id_base_visit
        ),
        organismes AS (
            SELECT
                v.id_base_visit,
                string_agg(DISTINCT bo.nom_organisme, ', ') AS nom_organisme
            FROM gn_monitoring.t_base_visits AS v
                JOIN gn_monitoring.cor_visit_observer AS observer
                    ON observer.id_base_visit = v.id_base_visit
                JOIN utilisateurs.t_roles AS roles
                    ON roles.id_role = observer.id_role
                JOIN utilisateurs.bib_organismes AS bo
                    ON bo.id_organisme = roles.id_organisme
            GROUP BY v.id_base_visit
        ),
        disturbances AS (
            SELECT
                v.id_base_visit,
                string_agg(n.label_default, ',') AS label_disturbance
            FROM gn_monitoring.t_base_visits AS v
                JOIN pr_monitoring_flora_station.cor_visit_disturbances AS p
                    ON v.id_base_visit = p.id_base_visit
                JOIN ref_nomenclatures.t_nomenclatures AS n
                    ON p.id_nomenclature_disturbance = n.id_nomenclature
            GROUP BY v.id_base_visit
        ),
        strates AS (
            SELECT
                id_base_visit,
                id_plot_survey,
                id_plot,
                json_object_agg(
                    label_default, cover_percentage ORDER BY label_default
                ) AS cover_strate,
                json_object_agg(
                    cd_nomenclature, cover_percentage ORDER BY cd_nomenclature
                ) AS cover_code_strate
            FROM (
                SELECT
                    v.id_base_visit,
                    n.label_default,
                    t.id_nomenclature_stratum,
                    t.cover_percentage,
                    r.id_plot_survey,
                    r.id_plot,
                    cd_nomenclature
                FROM gn_monitoring.t_base_visits AS v
                    JOIN pr_monitoring_flora_station.t_plot_surveys AS r
                        ON r.id_base_visit = v.id_base_visit
                    JOIN pr_monitoring_flora_station.cor_plot_survey_strata AS t
                        ON t.id_plot_survey = r.id_plot_survey
                    JOIN ref_nomenclatures.t_nomenclatures AS n
                        ON n.id_nomenclature = t.id_nomenclature_stratum
                WHERE t.cover_percentage IS NOT NULL
                GROUP BY v.id_base_visit, n.label_default, t.id_nomenclature_stratum, t.cover_percentage,
                    r.id_plot_survey, n.cd_nomenclature, r.id_plot
            ) AS s
            GROUP BY id_base_visit, id_plot_survey, id_plot
            ORDER BY id_base_visit
        ),
        substrates AS (
            SELECT
                id_base_visit,
                id_plot_survey,
                id_plot,
                json_object_agg(
                    label_default, cover_percentage ORDER BY label_default
                ) AS cover_substrate,
                json_object_agg(
                    cd_nomenclature, cover_percentage ORDER BY cd_nomenclature
                ) AS cover_code_substrate
            FROM (
                SELECT
                    v.id_base_visit,
                    n.label_default,
                    t.id_nomenclature_substrate,
                    t.cover_percentage,
                    r.id_plot_survey,
                    r.id_plot,
                    cd_nomenclature
                FROM gn_monitoring.t_base_visits AS v
                    JOIN pr_monitoring_flora_station.t_plot_surveys AS r
                        ON r.id_base_visit = v.id_base_visit
                    JOIN pr_monitoring_flora_station.cor_plot_survey_substrates AS t
                        ON t.id_plot_survey = r.id_plot_survey
                    JOIN ref_nomenclatures.t_nomenclatures AS n
                        ON n.id_nomenclature = t.id_nomenclature_substrate
                WHERE t.cover_percentage IS NOT NULL
                GROUP BY v.id_base_visit, n.label_default, t.id_nomenclature_substrate, t.cover_percentage,
                    r.id_plot_survey, n.cd_nomenclature, r.id_plot
            ) AS s
            GROUP BY id_base_visit, id_plot_survey, id_plot
            ORDER BY id_base_visit
        ),
        plot_disturbances AS (
            SELECT
                id_base_visit,
                id_plot_survey,
                string_agg(label_default, ',' ORDER BY label_default) AS label_plot_disturbance
            FROM (
                SELECT
                    v.id_base_visit,
                    n.label_default,
                    r.id_plot_survey
                FROM gn_monitoring.t_base_visits AS v
                    JOIN pr_monitoring_flora_station.t_plot_surveys AS r
                        ON r.id_base_visit = v.id_base_visit
                    JOIN pr_monitoring_flora_station.cor_plot_survey_disturbances AS t
                        ON t.id_plot_survey = r.id_plot_survey
                    JOIN ref_nomenclatures.t_nomenclatures AS n
                        ON n.id_nomenclature = t.id_nomenclature_disturbance
            ) AS s
            GROUP BY id_base_visit, id_plot_survey
        )
        SELECT sites.id_base_site AS idbsite,
            visits.id_base_visit AS idbvisit,
            visits.visit_date_min AS visitdate,
            releve.id_plot_survey AS idreleve,
            releve.is_exclosure AS isexclosure,
            releve.remarks AS remarks,
            releve.taxon_present AS taxonpresent,
            releve.flowering_stems_count AS floweringstems,
            releve.non_flowering_stems_count AS nonfloweringstems,
            plot.code_plot AS codeplot,
            per.label_disturbance AS lbdisturbance,
            plotper.label_plot_disturbance AS lbplotdisturbance,
            obs.observers,
            strate.cover_strate AS covstrate,
            strate.cover_code_strate AS covcodestrate,
            substrate.cover_substrate AS covsubstrate,
            substrate.cover_code_substrate AS covcodesubstrate,
            taxref.lb_nom AS lbtaxon,
            sta.cd_nom,
            transect.transect_label AS transectlb,
            transect.plot_size AS plotsize,
            nomenclature.label_default AS plotpos,
            transect.geom_start,
            transect.geom_end,
            sites.geom,
            org.nom_organisme
        FROM gn_monitoring.t_base_sites AS sites
            JOIN gn_monitoring.t_base_visits AS visits
                ON sites.id_base_site = visits.id_base_site
            JOIN observers AS obs
                ON obs.id_base_visit = visits.id_base_visit
            JOIN organismes AS org
                ON org.id_base_visit = visits.id_base_visit
            LEFT JOIN disturbances AS per
                ON per.id_base_visit = visits.id_base_visit
            JOIN pr_monitoring_flora_station.t_transects AS transect
                ON transect.id_base_site = sites.id_base_site
            JOIN pr_monitoring_flora_station.t_plot_surveys AS releve
                ON releve.id_base_visit = visits.id_base_visit
            LEFT JOIN strates AS strate
                ON strate.id_plot_survey = releve.id_plot_survey
            LEFT JOIN substrates AS substrate
                ON substrate.id_plot_survey = releve.id_plot_survey
            LEFT JOIN plot_disturbances AS plotper
                ON plotper.id_plot_survey = releve.id_plot_survey
            JOIN pr_monitoring_flora_station.t_plots AS plot
                ON plot.id_plot = releve.id_plot
            LEFT JOIN pr_monitoring_flora_station.t_stations AS sta
                ON sta.id_station = transect.id_station
            LEFT JOIN taxonomie.taxref AS taxref
                ON taxref.cd_nom = sta.cd_nom
            JOIN ref_nomenclatures.t_nomenclatures AS nomenclature
                ON nomenclature.id_nomenclature = transect.id_nomenclature_plot_position
        ORDER BY visits.visit_date_min, plot.distance_plot, plot.code_plot;
        """
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS pr_monitoring_flora_station.export_visits")