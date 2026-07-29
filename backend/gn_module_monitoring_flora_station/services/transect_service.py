import json
from flask import g

from geoalchemy2 import functions as geo_funcs
from geonature.utils.env import DB

from ..repositories.transect_repository import TransectRepository


class TransectService:
    """
    Règles métier pour les transects et les sites associés.
    """

    def __init__(self, transect_repo=None):
        self.transect_repo = transect_repo or TransectRepository()

    def get_transect(self, id_transect):
        return self.transect_repo.get_by_id(id_transect)

    def list_transects_by_station(self, id_station):
        return self.transect_repo.get_by_station(id_station)

    def delete_transect(self, id_transect):
        transect = self.transect_repo.get_by_id(id_transect)
        if transect is None:
            raise ValueError(f"Transect {id_transect} introuvable")
        self.transect_repo.delete(transect)

    def list_available_sites(self, site_type_code, id_base_site=None):
        sites = list(self.transect_repo.get_sites_without_transect(site_type_code))
        if id_base_site:
            current_site = self.transect_repo.get_site_by_id(id_base_site)
            if current_site:
                sites.append(current_site)
        return [s.as_dict() for s in sites]

    def build_transect_feature(self, id_site, municipality_type_code, module_code):
        data = self.transect_repo.get_transect_detail(id_site, municipality_type_code)
        if not data:
            return None

        transect = data[0].get_geofeature(fields=["t_base_site", "cor_plots"])
        transect["properties"]["plot_position"] = data[1].as_dict()
        if data[2]:
            transect["properties"]["nom_commune"] = str(data[2])
        if data[3]:
            transect["properties"]["observers"] = str(data[3])
        if data[4]:
            transect["properties"]["nom_taxon"] = str(data[4])

        id_digitiser = data[0].t_base_site.id_digitiser
        scope = self.transect_repo.get_edit_scope_info(module_code)
        can_edit = False
        if scope == 3:
            can_edit = True
        elif scope == 2:
            digitiser = self.transect_repo.get_digitiser(id_digitiser)
            if digitiser and digitiser.id_organisme == g.current_user.id_organisme:
                can_edit = True
        elif scope == 1:
            if id_digitiser == g.current_user.id_role:
                can_edit = True
        transect["properties"]["can_edit"] = can_edit

        if data[0].station:
            transect["properties"]["station_name"] = data[0].station.name

        base_site = transect["properties"]["t_base_site"]
        transect["properties"]["base_site_code"] = base_site["base_site_code"]
        transect["properties"]["base_site_description"] = base_site["base_site_description"]
        transect["properties"]["base_site_name"] = base_site["base_site_name"]
        transect["properties"]["uuid_base_site"] = str(base_site["uuid_base_site"])
        del transect["properties"]["t_base_site"]

        return transect

    def build_transects_query(self, filters):
        q = self.transect_repo.get_transects_list_query()

        if "filterTaxon" in filters:
            from ..models import SfsStation
            q = q.where(SfsStation.cd_nom == filters["filterTaxon"])

        q_date = None
        if "date_low" in filters and "date_up" in filters:
            from geonature.core.gn_monitoring.models import TBaseVisits
            from sqlalchemy import and_
            q_date = self.transect_repo.get_transects_date_query()
            q = q.where(
                and_(
                    TBaseVisits.visit_date_min <= filters["date_up"],
                    TBaseVisits.visit_date_min >= filters["date_low"],
                )
            )
        return q, q_date

    def create_transect_with_site(self, data, plots, sensors, module_code, site_type_code, create_plot_fn):
        from ..models import SfsTransect, SfsSensor

        site = self.transect_repo.create_site(
            transect_label=data.get("transect_label"),
            base_site_description=data.pop("base_site_description", None),
            geom_start=data.get("geom_start"),
            geom_end=data.get("geom_end"),
            module_code=module_code,
            site_type_code=site_type_code,
        )

        data["id_base_site"] = site.id_base_site
        transect = SfsTransect(**data)
        self.transect_repo.save(transect)

        for plot_data in plots:
            plot_data["id_transect"] = transect.id_transect
            create_plot_fn(plot_data)

        for sensor_data in sensors:
            sensor_data["id_transect"] = transect.id_transect
            sensor = SfsSensor(**sensor_data)
            self.transect_repo.save(sensor)

        if transect.id_station:
            self.transect_repo.update_station_centroid(transect.id_station)

        return site.id_base_site

    def update_transect_with_site(self, data, plots, create_plot_fn):
        from ..models import SfsTransect

        self.transect_repo.update_site(
            id_base_site=data.get("id_base_site"),
            base_site_description=data.pop("base_site_description", None),
            geom_start=data.get("geom_start"),
            geom_end=data.get("geom_end"),
        )

        transect = SfsTransect(**data)
        transect = self.transect_repo.merge(transect)

        for plot_data in plots:
            plot_data["id_transect"] = transect.id_transect
            if not plot_data.get("id_plot"):
                create_plot_fn(plot_data)

        if transect.id_station:
            self.transect_repo.update_station_centroid(transect.id_station)

        return data.get("id_base_site")

    def list_transects_by_station_detailed(self, id_station):
        q = self.transect_repo.get_transects_by_station_query(id_station)
        data = DB.session.execute(q).unique().all()

        result = []
        for d in data:
            transect = d[0].as_dict()
            transect["nb_visits"] = d[1]
            transect["last_visit"] = str(d[2]) if d[2] else "Aucune visite"
            if d[0].geom_start:
                transect["geom_start"] = json.loads(
                    DB.session.scalar(geo_funcs.ST_AsGeoJSON(d[0].geom_start))
                )
            if d[0].geom_end:
                transect["geom_end"] = json.loads(
                    DB.session.scalar(geo_funcs.ST_AsGeoJSON(d[0].geom_end))
                )
            result.append(transect)
        return result