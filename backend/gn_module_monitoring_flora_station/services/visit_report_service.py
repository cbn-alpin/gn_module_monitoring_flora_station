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
            "cor_releve_plot.cor_releve_perturbations.t_nomenclature",
            "cor_visit_perturbation.t_nomenclature",
            "observers",
        ]
        )
        digitiser = self.visit_report_repo.get_digitiser(data.id_digitiser)
        if digitiser:
            visit["id_organisme"] = digitiser.id_organisme

        for plot_survey in visit["cor_releve_plot"]:
            plot_survey["strata_survey"] = plot_survey.pop("cor_releve_strats", [])
            plot_survey["substrates_survey"] = plot_survey.pop("cor_releve_substrats", [])
            plot_survey["disturbances_survey"] = plot_survey.pop("cor_releve_perturbations", [])

        return visit

    def create_visit(self, data, module_code, metadata_code):
        from ..models import (
            MfsPlotSurvey,
            MfsVisit,
            MfsVisitDisturbance,
            MfsPlotSurveyStratum,
            MfsPlotSurveySubstrate,
            MfsPlotSurveyDisturbance,
        )

        self.check_year_visit(data["id_base_site"], data["visit_date_min"])

        plot_surveys = data.pop("plots", [])
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

        visit = MfsVisit(**data)

        for disturbance in disturbances:
            visit.cor_visit_perturbation.append(MfsVisitDisturbance(**disturbance))

        for plot_survey_data in plot_surveys:
            strata = plot_survey_data.pop("strata_survey", [])
            substrates = plot_survey_data.pop("substrates_survey", [])
            disturbances_survey = plot_survey_data.pop("disturbances_survey", [])

            plot_survey = MfsPlotSurvey(**plot_survey_data)

            for stratum in strata:
                if stratum.get("cover_percentage"):
                    plot_survey.cor_releve_strats.append(MfsPlotSurveyStratum(**stratum))

            for substrate in substrates:
                if substrate.get("cover_percentage"):
                    plot_survey.cor_releve_substrats.append(MfsPlotSurveySubstrate(**substrate))

            for disturbance in disturbances_survey:
                plot_survey.cor_releve_perturbations.append(MfsPlotSurveyDisturbance(**disturbance))

            visit.cor_releve_plot.append(plot_survey)

        observers = self.visit_report_repo.get_users_by_ids(observers_ids)
        for observer in observers:
            visit.observers.append(observer)

        return self.visit_report_repo.save_visit(visit)

    def update_visit(self, id_visit, data):
        from ..models import (
            MfsPlotSurvey,
            MfsVisit,
            MfsVisitDisturbance,
            MfsPlotSurveyStratum,
            MfsPlotSurveySubstrate,
            MfsPlotSurveyDisturbance,
        )

        existing_visit = self.visit_report_repo.get_visit_by_id(id_visit)
        if existing_visit is None:
            raise NotFound(f"Visit {id_visit} does not exist")

        existing_dict = existing_visit.as_dict()
        if data["visit_date_min"] != existing_dict["visit_date_min"]:
            self.check_year_visit(
                data["id_base_site"], data["visit_date_min"], id_base_visit=id_visit
            )

        plot_surveys = data.pop("plots", [])
        observers_ids = data.pop("observers", [])
        disturbances = data.pop("perturbations", [])

        visit = MfsVisit(**data)

        for plot_survey_data in plot_surveys:
            strata = plot_survey_data.pop("strata_survey", [])
            substrates = plot_survey_data.pop("substrates_survey", [])
            disturbances_survey = plot_survey_data.pop("disturbances_survey", [])

            plot_survey = MfsPlotSurvey(**plot_survey_data)

            for stratum in strata:
                if stratum.get("cover_percentage"):
                    plot_survey.cor_releve_strats.append(MfsPlotSurveyStratum(**stratum))
                elif "id_plot_survey_stratum" in stratum:
                    self.visit_report_repo.delete_stratum(stratum["id_plot_survey_stratum"])

            for substrate in substrates:
                if substrate.get("cover_percentage"):
                    plot_survey.cor_releve_substrats.append(MfsPlotSurveySubstrate(**substrate))
                elif "id_plot_survey_substrate" in substrate:
                    self.visit_report_repo.delete_substrate(
                        substrate["id_plot_survey_substrate"]
                    )

            self.visit_report_repo.delete_plot_disturbances(
                plot_survey_data.get("id_plot_survey")
            )
            for disturbance in disturbances_survey:
                plot_survey.cor_releve_perturbations.append(MfsPlotSurveyDisturbance(**disturbance))

            visit.cor_releve_plot.append(plot_survey)

        self.visit_report_repo.delete_visit_disturbances(id_visit)
        for disturbance in disturbances:
            visit.cor_visit_perturbation.append(MfsVisitDisturbance(**disturbance))

        observers = self.visit_report_repo.get_users_by_ids(observers_ids)
        for observer in observers:
            visit.observers.append(observer)

        return self.visit_report_repo.merge_visit(visit)