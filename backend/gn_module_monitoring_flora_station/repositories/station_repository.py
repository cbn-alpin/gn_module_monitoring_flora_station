
from sqlalchemy import select, func, distinct, and_, or_, desc

from geonature.utils.env import DB
from geonature.core.gn_monitoring.models import CorVisitObserver, TBaseVisits
from ref_geo.models import LAreas
from pypnusershub.db.models import User, Organisme
from apptax.taxonomie.models import Taxref
 

from ..models import MfsStation, MfsTransect


class StationRepository:
    """
    Accès BDD pur pour les stations.
    """

    def get_by_id(self, id_station):
        return DB.session.get(MfsStation, id_station)

    def get_all(self):
        return DB.session.query(MfsStation).all()

    def get_by_taxon(self, cd_nom):
        return DB.session.query(MfsStation).filter_by(cd_nom=cd_nom).all()

    def save(self, station):
        DB.session.add(station)
        DB.session.commit()
        return station

    def merge(self, station):
        merged = DB.session.merge(station)
        DB.session.commit()
        return merged

    def delete(self, station):
        DB.session.delete(station)
        DB.session.commit()

    def get_station_detail(self, id_station, municipality_type_code):
        return DB.session.execute(
            select(
                MfsStation,
                Taxref.lb_nom,
                func.string_agg(distinct(LAreas.area_name), ", "),
            )
            .filter_by(id_station=id_station)
            .outerjoin(Taxref, MfsStation.cd_nom == Taxref.cd_nom)
            .outerjoin(
                LAreas,
                and_(
                    func.ST_Intersects(func.ST_Transform(MfsStation.geom, 2154), LAreas.geom),
                    LAreas.id_type == func.ref_geo.get_id_area_type(municipality_type_code),
                ),
            )
            .group_by(MfsStation.id_station, Taxref.lb_nom)
        ).first()

    def get_stations_list_query(self, municipality_type_code):
        return (
            select(
                MfsStation,
                Taxref.lb_nom,
                func.count(distinct(TBaseVisits.id_base_visit)).label("nb_visits"),
                func.max(TBaseVisits.visit_date_min).label("last_visit"),
                func.count(distinct(MfsTransect.id_transect)).label("nb_transect"),
                func.string_agg(distinct(LAreas.area_name), ", "),
            )
            .outerjoin(Taxref, MfsStation.cd_nom == Taxref.cd_nom)
            .outerjoin(MfsTransect, MfsTransect.id_station == MfsStation.id_station)
            .outerjoin(TBaseVisits, TBaseVisits.id_base_site == MfsTransect.id_base_site)
            .outerjoin(
                LAreas,
                and_(
                    func.ST_Intersects(func.ST_Transform(MfsStation.geom, 2154), LAreas.geom),
                    LAreas.id_type == func.ref_geo.get_id_area_type(municipality_type_code),
                ),
            )
            .outerjoin(CorVisitObserver.__table__, CorVisitObserver.__table__.c.id_base_visit == TBaseVisits.id_base_visit)
            .outerjoin(User, User.id_role == CorVisitObserver.__table__.c.id_role)
            .outerjoin(Organisme, Organisme.id_organisme == User.id_organisme)
            .group_by(MfsStation.id_station, Taxref.lb_nom)
            .order_by(MfsStation.name)
        )

    def get_visit_years(self):
        q = (
            select(func.extract("year", TBaseVisits.visit_date_min).label("year"))
            .outerjoin(MfsTransect, MfsTransect.id_base_site == TBaseVisits.id_base_site)
            .outerjoin(MfsStation, MfsStation.id_station == MfsTransect.id_station)
            .where(TBaseVisits.visit_date_min != None)
            .distinct()
            .order_by(desc(func.extract("year", TBaseVisits.visit_date_min)))
        )
        return DB.session.execute(q).all()

    def get_areas(self, municipality_type_code):
        q = (
            select(LAreas.area_name)
            .select_from(MfsStation)
            .outerjoin(
                LAreas,
                and_(
                    func.ST_Intersects(func.ST_Transform(MfsStation.geom, 2154), LAreas.geom),
                    LAreas.id_type == func.ref_geo.get_id_area_type(municipality_type_code),
                ),
            )
            .where(LAreas.area_name != None)
            .distinct()
            .order_by(LAreas.area_name)
        )
        return DB.session.execute(q).all()

    def get_organisms(self):
        q = (
            select(Organisme.nom_organisme)
            .select_from(MfsStation)
            .outerjoin(MfsTransect, MfsTransect.id_station == MfsStation.id_station)
            .outerjoin(TBaseVisits, TBaseVisits.id_base_site == MfsTransect.id_base_site)
            .outerjoin(CorVisitObserver.__table__, CorVisitObserver.__table__.c.id_base_visit == TBaseVisits.id_base_visit)
            .outerjoin(User, User.id_role == CorVisitObserver.__table__.c.id_role)
            .outerjoin(Organisme, Organisme.id_organisme == User.id_organisme)
            .distinct()
        )
        return DB.session.execute(q).all()
    
    def get_distinct_taxa(self):
       
        q = (
            select(distinct(MfsStation.cd_nom), Taxref.lb_nom)
            .join(Taxref, MfsStation.cd_nom == Taxref.cd_nom)
            .order_by(Taxref.lb_nom)
        )
        return DB.session.execute(q).all()