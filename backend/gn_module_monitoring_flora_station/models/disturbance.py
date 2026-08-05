from .base import MonitoringFloreStation
from geonature.utils.env import DB
from geonature.core.gn_monitoring.models import TBaseVisits

from utils_flask_sqla.serializers import serializable
from pypnnomenclature.models import TNomenclatures


@serializable
class MfsPlotSurveyDisturbance(MonitoringFloreStation):
    __tablename__ = "cor_plot_survey_disturbances"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_plot_survey_disturbance = DB.Column(
        DB.Integer, primary_key=True, server_default=DB.FetchedValue()
    )
    id_plot_survey = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_plot_surveys.id_plot_survey",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    id_nomenclature_disturbance = DB.Column(
        DB.ForeignKey(
            "ref_nomenclatures.t_nomenclatures.id_nomenclature",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )

    t_nomenclature = DB.relationship(TNomenclatures)


@serializable
class MfsVisitDisturbance(MonitoringFloreStation):
    __tablename__ = "cor_visit_disturbances"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_visit_disturbance = DB.Column(
        DB.Integer, primary_key=True, server_default=DB.FetchedValue()
    )
    id_base_visit = DB.Column(
        DB.ForeignKey(
            "gn_monitoring.t_base_visits.id_base_visit",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    id_nomenclature_disturbance = DB.Column(
        DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature", onupdate="CASCADE"),
        nullable=False,
    )

    t_base_visit = DB.relationship(TBaseVisits)
    t_nomenclature = DB.relationship(TNomenclatures)