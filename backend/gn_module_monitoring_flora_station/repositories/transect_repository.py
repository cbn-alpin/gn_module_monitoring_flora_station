import datetime
from flask import g
from sqlalchemy import and_, distinct, func, update, select

from geonature.utils.env import DB
from geonature.core.gn_monitoring.models import (
    corVisitObserver,
    corSiteArea,
    TBaseVisits,
    TBaseSites,
)
from ref_geo.models import LAreas
from apptax.taxonomie.models import Taxref
from pypnnomenclature.models import TNomenclatures
from pypnusershub.db.models import Organisme, User
from geonature.core.gn_permissions.tools import get_scopes_by_action

from ..models import MfsTransect, MfsStation


class TransectRepository:
    """
    Accès BDD pur pour les transects et les sites qui leur sont associés.
  
    """

    def get_by_id(self, id_transect):
        return DB.session.get(MfsTransect, id_transect)

    def get_by_station(self, id_station):
        return DB.session.query(MfsTransect).filter_by(id_station=id_station).all()

    def save(self, transect):
        DB.session.add(transect)
        DB.session.commit()
        return transect

    def merge(self, transect):
        merged = DB.session.merge(transect)
        DB.session.commit()
        return merged

    def delete(self, transect):
        DB.session.delete(transect)
        DB.session.commit()

    def get_id_type_site(self, code):
        query = select(func.ref_nomenclatures.get_id_nomenclature("TYPE_SITE", code))
        return DB.session.execute(query).first()[0]

    def get_sites_without_transect(self, site_type_code):
        q = (
            select(TBaseSites)
            .outerjoin(MfsTransect, TBaseSites.id_base_site == MfsTransect.id_base_site)
            .where(
                and_(
                    TBaseSites.id_nomenclature_type_site == self.get_id_type_site(site_type_code),
                    MfsTransect.id_base_site == None,
                )
            )
        )
        return DB.session.scalars(q).unique().all()

    def get_site_by_id(self, id_base_site):
        return DB.session.scalars(
            select(TBaseSites).where(TBaseSites.id_base_site == id_base_site)
        ).first()

    def get_transect_detail(self, id_site, municipality_type_code):
        return DB.session.execute(
            select(
                MfsTransect,
                TNomenclatures,
                func.string_agg(distinct(LAreas.area_name), ", "),
                func.string_agg(distinct(Organisme.nom_organisme), ", "),
                Taxref.lb_nom,
            )
            .filter_by(id_base_site=id_site)
            .outerjoin(TBaseVisits, TBaseVisits.id_base_site == MfsTransect.id_base_site)
            .outerjoin(
                TNomenclatures,
                MfsTransect.id_nomenclature_plot_position == TNomenclatures.id_nomenclature,
            )
            .outerjoin(MfsStation, MfsTransect.id_station == MfsStation.id_station)
            .outerjoin(Taxref, MfsStation.cd_nom == Taxref.cd_nom)
            .outerjoin(corVisitObserver, corVisitObserver.c.id_base_visit == TBaseVisits.id_base_visit)
            .outerjoin(User, User.id_role == corVisitObserver.c.id_role)
            .outerjoin(Organisme, Organisme.id_organisme == User.id_organisme)
            .outerjoin(corSiteArea, corSiteArea.c.id_base_site == MfsTransect.id_base_site)
            .outerjoin(
                LAreas,
                and_(
                    LAreas.id_area == corSiteArea.c.id_area,
                    LAreas.id_type == func.ref_geo.get_id_area_type(municipality_type_code),
                ),
            )
            .group_by(MfsTransect.id_transect, TNomenclatures.id_nomenclature, Taxref.lb_nom)
        ).first()

    def get_edit_scope_info(self, module_code):
        return get_scopes_by_action(module_code=module_code)["U"]

    def get_digitiser(self, id_digitiser):
        return DB.session.get(User, id_digitiser)

    def get_transects_list_query(self):
        return (
            select(
                MfsTransect,
                func.max(TBaseVisits.visit_date_min),
                Taxref.lb_nom,
                func.count(distinct(TBaseVisits.id_base_visit)),
                func.string_agg(distinct(Organisme.nom_organisme), ", "),
            )
            .outerjoin(TBaseVisits, TBaseVisits.id_base_site == MfsTransect.id_base_site)
            .outerjoin(MfsStation, MfsTransect.id_station == MfsStation.id_station)
            .outerjoin(Taxref, MfsStation.cd_nom == Taxref.cd_nom)
            .outerjoin(corVisitObserver, corVisitObserver.c.id_base_visit == TBaseVisits.id_base_visit)
            .outerjoin(User, User.id_role == corVisitObserver.c.id_role)
            .outerjoin(Organisme, Organisme.id_organisme == User.id_organisme)
            .group_by(MfsTransect, Taxref.lb_nom)
        )

    def get_transects_date_query(self):
        return (
            select(
                MfsTransect.id_base_site,
                func.max(TBaseVisits.visit_date_min),
            )
            .outerjoin(TBaseVisits, TBaseVisits.id_base_site == MfsTransect.id_base_site)
            .group_by(MfsTransect.id_base_site)
        )

    def create_site(self, transect_label, base_site_description, geom_start, geom_end, module_code, site_type_code):
        site = TBaseSites(
            id_nomenclature_type_site=self.get_id_type_site(site_type_code),
            base_site_name=f"FLO - {module_code} - {transect_label}",
            base_site_description=base_site_description,
            first_use_date=datetime.datetime.now(),
            id_digitiser=g.current_user.id_role,
            geom=func.ST_MakeLine(geom_start, geom_end),
        )
        DB.session.add(site)
        DB.session.flush()
        site.base_site_code = f"FLO-{module_code}-{site.id_base_site}"
        return site

    def update_site(self, id_base_site, base_site_description, geom_start, geom_end):
        DB.session.execute(
            update(TBaseSites)
            .filter_by(id_base_site=id_base_site)
            .values(
                base_site_description=base_site_description,
                geom=func.ST_MakeLine(geom_start, geom_end).execution_options(
                    synchronize_session="fetch"
                ),
            )
        )

    def update_station_centroid(self, id_station):
        DB.session.execute(
            update(MfsStation)
            .where(MfsStation.id_station == id_station)
            .values(
                geom=DB.session.scalar(
                    select(func.ST_Centroid(func.ST_Collect(MfsTransect.geom_start))).where(
                        MfsTransect.id_station == id_station
                    )
                )
            )
        )

    def get_transects_by_station_query(self, id_station):
        return (
            select(
                MfsTransect,
                func.count(distinct(TBaseVisits.id_base_visit)).label("nb_visits"),
                func.max(TBaseVisits.visit_date_min).label("last_visit"),
            )
            .where(MfsTransect.id_station == id_station)
            .outerjoin(TBaseVisits, TBaseVisits.id_base_site == MfsTransect.id_base_site)
            .group_by(MfsTransect.id_transect)
        )