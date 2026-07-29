from .base import MonitoringFloreStation
from geonature.utils.env import DB

from utils_flask_sqla.serializers import serializable
from pypnnomenclature.models import TNomenclatures


@serializable
class SfsPlotSurveyStratum(MonitoringFloreStation):
    __tablename__ = "cor_plot_survey_strata"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_plot_survey_stratum = DB.Column(DB.Integer, primary_key=True, server_default=DB.FetchedValue())
    id_plot_survey = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_plot_surveys.id_plot_survey",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    id_nomenclature_stratum = DB.Column(
        DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature", onupdate="CASCADE"),
        nullable=False,
    )
    cover_percentage = DB.Column(DB.Integer)

    t_nomenclature = DB.relationship(TNomenclatures)


@serializable
class SfsPlotSurveySubstrate(MonitoringFloreStation):
    __tablename__ = "cor_plot_survey_substrates"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_plot_survey_substrate = DB.Column(
        DB.Integer, primary_key=True, server_default=DB.FetchedValue()
    )
    id_plot_survey = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_plot_surveys.id_plot_survey",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    id_nomenclature_substrate = DB.Column(
        DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature", onupdate="CASCADE"),
        nullable=False,
    )
    cover_percentage = DB.Column(DB.Integer)

    t_nomenclature = DB.relationship(TNomenclatures)