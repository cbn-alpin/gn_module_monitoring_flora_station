from .base import MonitoringFloreStation
from .transect import SfsTransect
from geonature.utils.env import DB, db

from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable
from geoalchemy2 import Geometry


@serializable
@geoserializable
class SfsStation(MonitoringFloreStation):
    __tablename__ = "t_stations"
    __table_args__ = {
        "schema": "pr_monitoring_flora_station",
    }
    id_station = DB.Column(
        DB.Integer, primary_key=True, server_default=DB.FetchedValue()
    )
    remarks = DB.Column(
        DB.Text,
        nullable=True,
    )
    name = DB.Column(
        DB.String(50),
        nullable=False
    )
    geom = DB.Column(
        Geometry("GEOMETRY", 4326)
    )
    cd_nom = DB.Column(
        DB.ForeignKey(
            "taxonomie.taxref.cd_nom",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    is_managed = DB.Column(
        DB.Boolean,
        nullable=True,
    )
    cor_transect = DB.relationship(SfsTransect, overlaps="station")