from sqlalchemy import func, or_

from geonature.core.gn_monitoring.models import TBaseVisits
from ref_geo.models import LAreas
from pypnusershub.db.models import User, Organisme

from ..models import MfsStation
from ..repositories.station_repository import StationRepository


class StationService:
    """
    Règles métier pour les stations.
    """

    def __init__(self, station_repo=None):
        self.station_repo = station_repo or StationRepository()

    def get_station(self, id_station):
        return self.station_repo.get_by_id(id_station)

    def list_stations(self):
        return self.station_repo.get_all()

    def list_stations_by_taxon(self, cd_nom):
        return self.station_repo.get_by_taxon(cd_nom)

    def create_station(self, station):
        return self.station_repo.save(station)

    def update_station(self, station):
        return self.station_repo.merge(station)

    def delete_station(self, id_station):
        station = self.station_repo.get_by_id(id_station)
        if station is None:
            raise ValueError(f"Station {id_station} introuvable")
        if station.cor_transect:
            raise ValueError(
                f"Impossible de supprimer la station {id_station} : elle a des transects rattachés"
            )
        self.station_repo.delete(station)

    def build_station_feature(self, id_station, municipality_type_code):
        data = self.station_repo.get_station_detail(id_station, municipality_type_code)
        if not data:
            return None
        feature = data[0].as_geofeature("geom", "id_station")
        if data[1]:
            feature["properties"]["taxon_name"] = str(data[1])
        if data[2]:
            feature["properties"]["nom_commune"] = str(data[2])
        return feature

    def build_stations_feature_collection(self, filters, municipality_type_code):
        q = self.station_repo.get_stations_list_query(municipality_type_code)

        if "filterTaxon" in filters:
            q = q.where(MfsStation.cd_nom == filters["filterTaxon"])
        if "year" in filters:
            q = q.where(func.extract("year", TBaseVisits.visit_date_min) == filters["year"])
        if "area_name" in filters:
            q = q.where(LAreas.area_name == filters["area_name"])
        if "observer" in filters:
            q = q.where(
                or_(
                    User.nom_role == filters["observer"],
                    User.prenom_role == filters["observer"],
                )
            )
        if "organism" in filters:
            q = q.where(Organisme.nom_organisme == filters["organism"])

        return q

    def get_visit_years(self):
        data = self.station_repo.get_visit_years()
        return [int(row[0]) for row in data if row[0] is not None]

    def get_areas(self, municipality_type_code):
        data = self.station_repo.get_areas(municipality_type_code)
        return [row[0] for row in data if row[0] is not None]

    def get_organisms(self):
        data = self.station_repo.get_organisms()
        return [row[0] for row in data if row[0] is not None]
    
    def get_taxa(self):
        data = self.station_repo.get_distinct_taxa()
        return [{"cd_nom": row[0], "lb_nom": row[1]} for row in data]

    