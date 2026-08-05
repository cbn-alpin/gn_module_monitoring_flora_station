from .base import MonitoringFloreStation
from geonature.utils.env import DB
from geoalchemy2 import Geometry

from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable


@serializable
@geoserializable
class ExportVisits(MonitoringFloreStation):
    __tablename__ = "export_visits"
    __table_args__ = {
        "schema": "pr_monitoring_flora_station",
    }

    idbsite = DB.Column(DB.Integer)
    idbvisit = DB.Column(DB.Integer)
    visitdate = DB.Column(DB.DateTime)
    idreleve = DB.Column(DB.Integer, primary_key=True)
    isexclosure = DB.Column(DB.Boolean)
    remarks = DB.Column(DB.Unicode)
    taxonpresent = DB.Column(DB.Boolean)
    floweringstems = DB.Column(DB.Integer)
    nonfloweringstems = DB.Column(DB.Integer)
    codeplot = DB.Column(DB.Unicode)
    lbdisturbance = DB.Column(DB.Unicode)
    lbplotdisturbance = DB.Column(DB.Unicode)
    observers = DB.Column(DB.Unicode)
    covstrate = DB.Column(DB.Unicode)
    covcodestrate = DB.Column(DB.Unicode)
    covsubstrate = DB.Column(DB.Unicode)
    covcodesubstrate = DB.Column(DB.Unicode)
    lbtaxon = DB.Column(DB.Unicode)
    cd_nom = DB.Column(DB.Integer)
    transectlb = DB.Column(DB.Unicode)
    plotsize = DB.Column(DB.Integer)
    plotpos = DB.Column(DB.Unicode)
    geom_start = DB.Column(Geometry("GEOMETRY", 4326))
    geom_end = DB.Column(Geometry("GEOMETRY", 4326))
    geom = DB.Column(Geometry("GEOMETRY", 4326))
    nom_organisme = DB.Column(DB.Unicode)