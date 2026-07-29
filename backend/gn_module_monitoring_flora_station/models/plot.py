from .base import MonitoringFloreStation
from geonature.utils.env import DB, db

from utils_flask_sqla.serializers import serializable


@serializable
class SfsPlot(MonitoringFloreStation):
    __tablename__ = "t_plots"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_plot = DB.Column(DB.Integer, primary_key=True, server_default=DB.FetchedValue())
    id_transect = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_transects.id_transect",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    code_plot = DB.Column(DB.String(50), nullable=False)
    distance_plot = DB.Column(DB.Integer)
    id_parent = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_plots.id_plot",
            ondelete="CASCADE",
        ),
    )
    parent = DB.relationship(
        "gn_module_monitoring_flora_station.models.plot.SfsPlot", remote_side=[id_plot]
    )
    sub_plots = DB.relationship(
        "gn_module_monitoring_flora_station.models.plot.SfsPlot",
        foreign_keys=[id_parent],
        passive_deletes=True,
        overlaps="parent",
    )