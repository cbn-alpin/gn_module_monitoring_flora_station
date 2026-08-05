from .base import MonitoringFloreStation
from .plot import MfsPlot
from geonature.utils.env import DB, db
from geonature.core.gn_monitoring.models import TBaseVisits

from utils_flask_sqla.serializers import serializable

from .disturbance import MfsVisitDisturbance


@serializable
class MfsPlotSurvey(MonitoringFloreStation):
    __tablename__ = "t_plot_surveys"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_plot_survey = DB.Column(DB.Integer, primary_key=True, server_default=DB.FetchedValue())
    id_plot = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_plots.id_plot",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    id_base_visit = DB.Column(
        DB.ForeignKey(
            "gn_monitoring.t_base_visits.id_base_visit",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    is_exclosure = DB.Column(DB.Boolean)
    remarks = DB.Column(DB.Text)
    taxon_present = DB.Column(DB.Boolean)
    flowering_stems_count = DB.Column(DB.Integer)
    non_flowering_stems_count = DB.Column(DB.Integer)

    cor_releve_strats = DB.relationship(
        "gn_module_monitoring_flora_station.models.cover.MfsPlotSurveyStratum",
        backref="id_plot_survey_s",
    )
    cor_releve_substrats = DB.relationship(
        "gn_module_monitoring_flora_station.models.cover.MfsPlotSurveySubstrate",
        backref="id_plot_survey_sub",
    )
    cor_releve_perturbations = DB.relationship(
        "gn_module_monitoring_flora_station.models.disturbance.MfsPlotSurveyDisturbance",
        backref="id_plot_survey_p",
    )

    t_base_visit = DB.relationship(TBaseVisits)
    t_plot = DB.relationship(
        "gn_module_monitoring_flora_station.models.plot.MfsPlot"
    )


@serializable
class MfsVisit(TBaseVisits):
    __tablename__ = "t_base_visits"
    __table_args__ = {"schema": "gn_monitoring", "extend_existing": True}

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    cor_visit_perturbation = DB.relationship(MfsVisitDisturbance, backref="t_base_visits")
    cor_releve_plot = DB.relationship(MfsPlotSurvey, backref="t_base_visits")