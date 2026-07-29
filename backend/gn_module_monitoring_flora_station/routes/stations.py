
from flask import request
from geojson import FeatureCollection
from sqlalchemy import select, func

from geonature.utils.env import DB
from geonature.core.gn_permissions import decorators as permissions
from utils_flask_sqla.response import json_resp

from ..blueprint import blueprint
from ..models import SfsStation
from ..services.station_service import StationService
from gn_module_monitoring_flora_station import MODULE_CODE

station_service = StationService()


@blueprint.route("/stations", methods=["POST"])
@permissions.check_cruved_scope("C", get_scope=True, module_code=MODULE_CODE)
@json_resp
def add_station(scope):
    data = dict(request.get_json())
    try:
        station = SfsStation(**data)
        station_service.create_station(station)
        return station_service.build_station_feature(
            station.id_station, blueprint.config["municipality_type_code"]
        )
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/stations", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_all_stations():
    parameters = request.args
    municipality_type_code = blueprint.config["municipality_type_code"]

    q = station_service.build_stations_feature_collection(parameters, municipality_type_code)

    page = request.args.get("page", 1, type=int)
    items_per_page = blueprint.config["items_per_page"]
    pagination_serverside = blueprint.config["pagination_serverside"]
    total_items = DB.session.scalar(select(func.count("*")).select_from(q))

    if pagination_serverside:
        data = DB.session.execute(q.limit(items_per_page).offset(page * items_per_page)).unique().all()
    else:
        data = DB.session.execute(q).unique().all()

    page_info = {
        "totalItems": total_items,
        "itemsPerPage": items_per_page,
    }
    if data:
        features = []
        for d in data:
            feature = d[0].as_geofeature("geom", "id_station")
            feature["properties"]["taxon_name"] = str(d[1])
            feature["properties"]["nb_visits"] = d[2]
            feature["properties"]["last_visit"] = str(d[3]) if d[3] else "Aucune visite"
            feature["properties"]["nb_transect"] = d[4]
            feature["properties"]["commune_name"] = d[5]
            features.append(feature)
        return [page_info, FeatureCollection(features)]
    return None


@blueprint.route("/stations/years", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_years_visits():
    return station_service.get_visit_years()


@blueprint.route("/stations/area", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_area():
    return station_service.get_areas(blueprint.config["municipality_type_code"])


@blueprint.route("/stations/organism", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_organism():
    return station_service.get_organisms()


@blueprint.route("/stations/<id_station>", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_one_station(id_station):
    return station_service.build_station_feature(
        id_station, blueprint.config["municipality_type_code"]
    )


@blueprint.route("/stations/<id_station>", methods=["PATCH"])
@permissions.check_cruved_scope("U", get_scope=True, module_code=MODULE_CODE)
@json_resp
def update_station(id_station, scope):
    data = dict(request.get_json())
    try:
        station = SfsStation(**data)
        station = station_service.update_station(station)
        return station_service.build_station_feature(
            station.id_station, blueprint.config["municipality_type_code"]
        )
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/stations/<id_station>", methods=["DELETE"])
@permissions.check_cruved_scope("D", module_code=MODULE_CODE)
@json_resp
def delete_station(id_station):
    try:
        station_service.delete_station(id_station)
        return {"message": "Station deleted successfully"}
    except ValueError as e:
        return {"error": str(e)}, 404
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500