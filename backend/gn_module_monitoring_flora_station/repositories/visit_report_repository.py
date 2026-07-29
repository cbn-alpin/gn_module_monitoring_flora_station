
from sqlalchemy import select, func, delete

from geonature.core.gn_meta.models import TDatasets
from geonature.core.gn_commons.models import TModules
from geonature.core.gn_monitoring.models import TBaseVisits
from pypnusershub.db.models import User
from geonature.utils.env import DB

from ..models import (
    SfsPlotSurvey,
    SfsVisit,
    SfsVisitDisturbance,
    SfsPlotSurveyStratum,
    SfsPlotSurveySubstrate,
    SfsPlotSurveyDisturbance,
)


class VisitReportRepository:
    """
    Accès BDD pur pour les relevés de placette, les visites, et les perturbations
    qui leur sont rattachées 
    
    """

    # --- Relevés de placette ---

    def get_by_id(self, id_plot_survey):
        return DB.session.get(SfsPlotSurvey, id_plot_survey)

    def get_by_plot(self, id_plot):
        return DB.session.query(SfsPlotSurvey).filter_by(id_plot=id_plot).all()

    def get_by_visit(self, id_base_visit):
        return DB.session.query(SfsPlotSurvey).filter_by(id_base_visit=id_base_visit).all()

    def save(self, plot_survey):
        DB.session.add(plot_survey)
        DB.session.commit()
        return plot_survey

    def merge(self, plot_survey):
        merged = DB.session.merge(plot_survey)
        DB.session.commit()
        return merged

    def delete(self, plot_survey):
        DB.session.delete(plot_survey)
        DB.session.commit()

    # --- Contrainte "une visite par an" ---

    def get_visit_years_for_site(self, id_base_site, exclude_visit_id=None):
        query = select(func.date_part("year", TBaseVisits.visit_date_min)).where(
            TBaseVisits.id_base_site == id_base_site
        )
        if exclude_visit_id is not None:
            query = query.where(TBaseVisits.id_base_visit != exclude_visit_id)
        return DB.session.execute(query).all()

    # --- Visites ---

    def get_visits_by_site_query(self, id_site):
        return select(SfsVisit).filter_by(id_base_site=id_site).order_by(SfsVisit.visit_date_min.desc())

    def count(self, query):
        return DB.session.scalar(select(func.count("*")).select_from(query))

    def get_visit_detail(self, id_visit):
        return DB.session.scalars(select(SfsVisit).filter_by(id_base_visit=id_visit)).first()

    def get_dataset_by_shortname(self, code):
        return DB.session.scalars(
            select(TDatasets).where(TDatasets.dataset_shortname == code)
        ).first()

    def get_module_id(self, module_code):
        return DB.session.execute(
            select(TModules.id_module).where(TModules.module_code == module_code)
        ).scalar_one()

    def get_users_by_ids(self, ids):
        return DB.session.scalars(select(User).where(User.id_role.in_(ids))).unique().all()

    def get_digitiser(self, id_digitiser):
        return DB.session.get(User, id_digitiser)

    def save_visit(self, visit):
        DB.session.add(visit)
        DB.session.commit()
        return visit

    def merge_visit(self, visit):
        merged = DB.session.merge(visit)
        DB.session.commit()
        return merged

    # --- Recouvrement / perturbations ---

    def delete_stratum(self, id_plot_survey_stratum):
        DB.session.execute(
            delete(SfsPlotSurveyStratum).filter_by(id_plot_survey_stratum=id_plot_survey_stratum)
        )

    def delete_substrate(self, id_plot_survey_substrate):
        DB.session.execute(
            delete(SfsPlotSurveySubstrate).filter_by(id_plot_survey_substrate=id_plot_survey_substrate)
        )

    def delete_visit_disturbances(self, id_visit):
        DB.session.execute(
            delete(SfsVisitDisturbance).filter_by(id_base_visit=id_visit)
        )

    def delete_plot_disturbances(self, id_plot_survey):
        DB.session.execute(
            delete(SfsPlotSurveyDisturbance).filter_by(id_plot_survey=id_plot_survey)
        )

    def get_visit_disturbances(self, id_base_visit):
        return (
            DB.session.query(SfsVisitDisturbance)
            .filter_by(id_base_visit=id_base_visit)
            .all()
        )

    def save_visit_disturbance(self, disturbance):
        DB.session.add(disturbance)
        DB.session.commit()
        return disturbance

    def get_plot_disturbances(self, id_plot_survey):
        return (
            DB.session.query(SfsPlotSurveyDisturbance)
            .filter_by(id_plot_survey=id_plot_survey)
            .all()
        )

    def save_plot_disturbance(self, disturbance):
        DB.session.add(disturbance)
        DB.session.commit()
        return disturbance