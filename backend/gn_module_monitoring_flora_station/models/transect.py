
from .base import MonitoringFloreStation
from geonature.utils.env import DB, db

from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable, shapeserializable
from geoalchemy2 import Geometry
import geoalchemy2.functions as geo_funcs
from geojson import Feature, LineString


@serializable
@geoserializable
class MfsTransect(MonitoringFloreStation):
    __tablename__ = "t_transects"
    __table_args__ = {"schema": "pr_monitoring_flora_station"}

    id_transect = DB.Column(DB.Integer, primary_key=True, server_default=DB.FetchedValue())
    id_base_site = DB.Column(
        DB.ForeignKey(
            "gn_monitoring.t_base_sites.id_base_site",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    transect_label = DB.Column(DB.String(50))
    geom_start = DB.Column(Geometry("POINT", 4326))
    geom_end = DB.Column(Geometry("POINT", 4326))
    id_nomenclature_plot_position = DB.Column(DB.Integer, nullable=False)
    plot_size = DB.Column(DB.String(50))
    plot_shape = DB.Column(DB.Unicode())
    id_station = DB.Column(
        DB.ForeignKey(
            "pr_monitoring_flora_station.t_stations.id_station",
            onupdate="CASCADE",
            ondelete="SET NULL",
        )
    )
    azimuth = DB.Column(
        DB.Integer,
        nullable=True,
    )

    t_base_site = DB.relationship("TBaseSites")
    cor_plots = DB.relationship(
        "gn_module_monitoring_flora_station.models.plot.MfsPlot", passive_deletes=True
    )
    station = DB.relationship(
        "gn_module_monitoring_flora_station.models.station.MfsStation", overlaps="cor_transect"
    )

    def get_geofeature(self, fields=[]):
        line = self.points_to_linestring()
        feature = Feature(
            id=str(self.id_base_site),
            geometry=line,
            properties=self.as_dict(fields=fields),
        )
        return feature

    def points_to_linestring(self):
        point1 = (
            DB.session.scalar(geo_funcs.ST_X(self.geom_start)),
            DB.session.scalar(geo_funcs.ST_Y(self.geom_start)),
        )
        point2 = (
            DB.session.scalar(geo_funcs.ST_X(self.geom_end)),
            DB.session.scalar(geo_funcs.ST_Y(self.geom_end)),
        )
        return LineString([point1, point2])