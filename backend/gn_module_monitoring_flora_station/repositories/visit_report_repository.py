
from sqlalchemy import select, func, delete

from geonature.core.gn_meta.models import TDatasets
from geonature.core.gn_commons.models import TModules
from geonature.core.gn_monitoring.models import TBaseVisits
from pypnusershub.db.models import User
from geonature.utils.env import DB

from ..models import (
    MfsPlotSurvey,
    MfsVisit,
    MfsVisitDisturbance,
    MfsPlotSurveyStratum,
    MfsPlotSurveySubstrate,
    MfsPlotSurveyDisturbance,
)


class VisitReportRepository:
    """
    Accès BDD pur pour les relevés de placette, les visites, et les perturbations
    qui leur sont rattachées 
    
    """

    #Relevés de placette

    def get_by_id(self, id_plot_survey):
        return DB.session.get(MfsPlotSurvey, id_plot_survey)

    def get_by_plot(self, id_plot):
        return DB.session.query(MfsPlotSurvey).filter_by(id_plot=id_plot).all()

    def get_by_visit(self, id_base_visit):
        return DB.session.query(MfsPlotSurvey).filter_by(id_base_visit=id_base_visit).all()

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

    #Contrainte "une visite par an"

    def get_visit_years_for_site(self, id_base_site, exclude_visit_id=None):
        query = select(func.date_part("year", TBaseVisits.visit_date_min)).where(
            TBaseVisits.id_base_site == id_base_site
        )
        if exclude_visit_id is not None:
            query = query.where(TBaseVisits.id_base_visit != exclude_visit_id)
        return DB.session.execute(query).all()

    # Visites

    def get_visits_by_site_query(self, id_site):
        return select(MfsVisit).filter_by(id_base_site=id_site).order_by(MfsVisit.visit_date_min.desc())

    def count(self, query):
        return DB.session.scalar(select(func.count("*")).select_from(query))

    def get_visit_detail(self, id_visit):
        return DB.session.scalars(select(MfsVisit).filter_by(id_base_visit=id_visit)).first()

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

    #Recouvrement / perturbations

    def delete_stratum(self, id_plot_survey_stratum):
        DB.session.execute(
            delete(MfsPlotSurveyStratum).filter_by(id_plot_survey_stratum=id_plot_survey_stratum)
        )

    def delete_substrate(self, id_plot_survey_substrate):
        DB.session.execute(
            delete(MfsPlotSurveySubstrate).filter_by(id_plot_survey_substrate=id_plot_survey_substrate)
        )

    def delete_visit_disturbances(self, id_visit):
        DB.session.execute(
            delete(MfsVisitDisturbance).filter_by(id_base_visit=id_visit)
        )

    def delete_plot_disturbances(self, id_plot_survey):
        DB.session.execute(
            delete(MfsPlotSurveyDisturbance).filter_by(id_plot_survey=id_plot_survey)
        )

    def get_visit_disturbances(self, id_base_visit):
        return (
            DB.session.query(MfsVisitDisturbance)
            .filter_by(id_base_visit=id_base_visit)
            .all()
        )
    def get_visit_by_id(self, id_base_visit):
        return DB.session.get(MfsVisit, id_base_visit)

    def save_visit_disturbance(self, disturbance):
        DB.session.add(disturbance)
        DB.session.commit()
        return disturbance

    def get_plot_disturbances(self, id_plot_survey):
        return (
            DB.session.query(MfsPlotSurveyDisturbance)
            .filter_by(id_plot_survey=id_plot_survey)
            .all()
        )

    def save_plot_disturbance(self, disturbance):
        DB.session.add(disturbance)
        DB.session.commit()
        return disturbance

    def get_export_query(self, filters):
        from sqlalchemy import select, func
        from ..models import ExportVisits

        query = select(ExportVisits)

        if "id_base_site" in filters:
            query = query.where(ExportVisits.idbsite == filters["id_base_site"])
        if "id_base_visit" in filters:
            query = query.where(ExportVisits.idbvisit == filters["id_base_visit"])
        if "id_plot_survey" in filters:
            query = query.where(ExportVisits.idreleve == filters["id_plot_survey"])
        if "year" in filters:
            query = query.where(func.date_part("year", ExportVisits.visitdate) == filters["year"])
        if "filterTaxon" in filters:
            query = query.where(ExportVisits.cd_nom == filters["filterTaxon"])
        if "organism" in filters:
            query = query.where(ExportVisits.nom_organisme.ilike(f"%{filters['organism']}%"))

        return DB.session.scalars(query).all()

    def get_strate_list_for_export(self):
        from sqlalchemy import select
        from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes

        query = select(TNomenclatures.label_default).join(
            BibNomenclaturesTypes, BibNomenclaturesTypes.id_type == TNomenclatures.id_type
        ).where(BibNomenclaturesTypes.mnemonique == "STRATE_PLACETTE")
        return [row[0] for row in DB.session.execute(query).all()]

    def get_substrate_list_for_export(self):
        from sqlalchemy import select
        from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes

        query = select(TNomenclatures.label_default).join(
            BibNomenclaturesTypes, BibNomenclaturesTypes.id_type == TNomenclatures.id_type
        ).where(BibNomenclaturesTypes.mnemonique == "SUBSTRAT_PLACETTE")
        return [row[0] for row in DB.session.execute(query).all()]