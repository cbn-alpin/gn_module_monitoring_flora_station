from flask import g
from werkzeug.exceptions import NotFound, BadRequest

from ..repositories.visit_report_repository import VisitReportRepository


class PostYearError(BadRequest):
    pass


class VisitReportService:
    """
    Règles métier pour les relevés de placette et les visites.
    """

    def __init__(self, visit_report_repo=None):
        self.visit_report_repo = visit_report_repo or VisitReportRepository()

    def get_visit_report(self, id_plot_survey):
        return self.visit_report_repo.get_by_id(id_plot_survey)

    def list_reports_by_plot(self, id_plot):
        return self.visit_report_repo.get_by_plot(id_plot)

    def list_reports_by_visit(self, id_base_visit):
        return self.visit_report_repo.get_by_visit(id_base_visit)

    def check_year_visit(self, id_base_site, new_visit_date, id_base_visit=None):
        """
        Vérifie qu'il n'existe pas déjà une visite la même année sur ce site.
        """
        old_years = self.visit_report_repo.get_visit_years_for_site(id_base_site, id_base_visit)
        year_new_visit = new_visit_date[0:4]
        for year in old_years:
            if str(int(year[0])) == year_new_visit:
                raise PostYearError(
                    f"Le site {id_base_site} a déjà été visité en {year_new_visit}"
                )

    def list_visits_by_site(self, id_site, items_per_page):
        from geonature.utils.env import DB

        query = self.visit_report_repo.get_visits_by_site_query(id_site)
        total_items = self.visit_report_repo.count(query)
        data = DB.session.scalars(query).unique().all()

        page_info = {"totalItems": total_items, "itemsPerPage": items_per_page}
        fields = ["cor_releve_plot", "cor_visit_perturbation", "observers"]
        if data:
            return [page_info, [d.as_dict(fields=fields) for d in data]]
        return None

    def build_visit_detail(self, id_visit):
        data = self.visit_report_repo.get_visit_detail(id_visit)
        if not data:
            return None

        visit = data.as_dict(
            fields=[
                "cor_releve_plot.cor_releve_strats",
                "cor_releve_plot.cor_releve_substrats",
                "cor_releve_plot.cor_releve_perturbations",
                "cor_visit_perturbation.t_nomenclature",
                "observers",
            ]
        )
        digitiser = self.visit_report_repo.get_digitiser(data.id_digitiser)
        if digitiser:
            visit["id_organisme"] = digitiser.id_organisme

        for releve in visit["cor_releve_plot"]:
            plot_data = {}
            for field in ("is_exclosure", "remarks", "taxon_present", "flowering_stems_count", "non_flowering_stems_count"):
                if field in releve:
                    plot_data[field] = releve.pop(field)
            if "cor_releve_strats" in releve:
                plot_data["strata_survey"] = releve.pop("cor_releve_strats")
            if "cor_releve_substrats" in releve:
                plot_data["substrates_survey"] = releve.pop("cor_releve_substrats")
            if "cor_releve_perturbations" in releve:
                plot_data["disturbances_survey"] = releve.pop("cor_releve_perturbations")
            releve["plot_data"] = plot_data

        return visit

    def create_visit(self, data, module_code, metadata_code):
        from ..models import (
            SfsPlotSurvey, SfsVisit, SfsVisitDisturbance,
            SfsPlotSurveyStratum, SfsPlotSurveySubstrate, SfsPlotSurveyDisturbance,
        )

        self.check_year_visit(data["id_base_site"], data["visit_date_min"])

        releve_plots = data.pop("plots", [])
        observers_ids = data.pop("observers", [])
        disturbances = data.pop("perturbations", None) or []

        if not data.get("id_dataset"):
            dataset = self.visit_report_repo.get_dataset_by_shortname(metadata_code)
            if not dataset:
                raise BadRequest(f"Module dataset shortname '{metadata_code}' was not found !")
            data["id_dataset"] = dataset.id_dataset

        if not data.get("id_module"):
            data["id_module"] = self.visit_report_repo.get_module_id(module_code)

        if not data.get("id_digitiser"):
            data["id_digitiser"] = g.current_user.id_role

        visit = SfsVisit(**data)

        for dist in disturbances:
            visit.cor_visit_perturbation.append(SfsVisitDisturbance(**dist))

        for releve in releve_plots:
            plot_data = releve.pop("plot_data", {})
            releve.update({
                "is_exclosure": plot_data.get("is_exclosure"),
                "remarks": plot_data.get("remarks"),
                "taxon_present": plot_data.get("taxon_present"),
                "flowering_stems_count": plot_data.get("flowering_stems_count"),
                "non_flowering_stems_count": plot_data.get("non_flowering_stems_count"),
            })
            plot_survey = SfsPlotSurvey(**releve)

            for stratum in plot_data.get("strata_survey", []):
                if stratum.get("cover_percentage"):
                    plot_survey.cor_releve_strats.append(SfsPlotSurveyStratum(**stratum))
            for substrate in plot_data.get("substrates_survey", []):
                if substrate.get("cover_percentage"):
                    plot_survey.cor_releve_substrats.append(SfsPlotSurveySubstrate(**substrate))
            for disturbance in plot_data.get("disturbances_survey", []):
                plot_survey.cor_releve_perturbations.append(SfsPlotSurveyDisturbance(**disturbance))

            visit.cor_releve_plot.append(plot_survey)

        observers = self.visit_report_repo.get_users_by_ids(observers_ids)
        for observer in observers:
            visit.observers.append(observer)

        return self.visit_report_repo.save_visit(visit)

    def update_visit(self, id_visit, data):
        from ..models import (
            SfsPlotSurvey, SfsVisit, SfsVisitDisturbance,
            SfsPlotSurveyStratum, SfsPlotSurveySubstrate, SfsPlotSurveyDisturbance,
        )

        existing_visit = self.visit_report_repo.get_by_id(id_visit)
        if existing_visit is None:
            raise NotFound(f"Visit {id_visit} does not exist")

        existing_dict = existing_visit.as_dict()
        if data["visit_date_min"] != existing_dict["visit_date_min"]:
            self.check_year_visit(data["id_base_site"], data["visit_date_min"], id_base_visit=id_visit)

        releve_plots = data.pop("plots", [])
        observers_ids = data.pop("observers", [])
        disturbances = data.pop("perturbations", [])

        visit = SfsVisit(**data)

        for releve in releve_plots:
            plot_data = releve.pop("plot_data", {})
            releve.update({
                "is_exclosure": plot_data.get("is_exclosure"),
                "remarks": plot_data.get("remarks"),
                "taxon_present": plot_data.get("taxon_present"),
                "flowering_stems_count": plot_data.get("flowering_stems_count"),
                "non_flowering_stems_count": plot_data.get("non_flowering_stems_count"),
            })
            plot_survey = SfsPlotSurvey(**releve)

            for stratum in plot_data.get("strata_survey", []):
                if stratum.get("cover_percentage"):
                    plot_survey.cor_releve_strats.append(SfsPlotSurveyStratum(**stratum))
                elif "id_plot_survey_stratum" in stratum:
                    self.visit_report_repo.delete_stratum(stratum["id_plot_survey_stratum"])

            for substrate in plot_data.get("substrates_survey", []):
                if substrate.get("cover_percentage"):
                    plot_survey.cor_releve_substrats.append(SfsPlotSurveySubstrate(**substrate))
                elif "id_plot_survey_substrate" in substrate:
                    self.visit_report_repo.delete_substrate(substrate["id_plot_survey_substrate"])

            self.visit_report_repo.delete_plot_disturbances(releve.get("id_plot_survey"))
            for disturbance in plot_data.get("disturbances_survey", []):
                plot_survey.cor_releve_perturbations.append(SfsPlotSurveyDisturbance(**disturbance))

            visit.cor_releve_plot.append(plot_survey)

        self.visit_report_repo.delete_visit_disturbances(id_visit)
        for disturbance in disturbances:
            visit.cor_visit_perturbation.append(SfsVisitDisturbance(**disturbance))

        observers = self.visit_report_repo.get_users_by_ids(observers_ids)
        for observer in observers:
            visit.observers.append(observer)

        return self.visit_report_repo.merge_visit(visit)