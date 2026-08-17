from flask import request,g
from geojson import FeatureCollection
from sqlalchemy import select, func

from geonature.utils.env import DB
from geonature.core.gn_permissions import decorators as permissions
from utils_flask_sqla.response import json_resp
from pypnusershub.db.tools import InsufficientRightsError
from pypnusershub.db.models import User

from ..blueprint import blueprint
from ..services.transect_service import TransectService
from gn_module_monitoring_flora_station import MODULE_CODE
from ..services.permission_service import PermissionService
from .plots import create_plot

transect_service = TransectService()
permission_service = PermissionService()


@blueprint.route("/sites", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_all_sites():
    parameters = request.args
    id_base_site = parameters.get("id_base_site")
    data = transect_service.list_available_sites(blueprint.config["site_type_code"], id_base_site)
    if data:
        return data
    return ("sites_not_found"), 404


@blueprint.route("/transects", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_all_transects():
    parameters = request.args
    q, q_date = transect_service.build_transects_query(parameters)

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
            feature = d[0].get_geofeature(fields=["t_base_site"])
            id_site = feature["properties"]["id_base_site"]
            base_site = feature["properties"]["t_base_site"]
            base_site_code = base_site["base_site_code"]
            base_site_description = base_site["base_site_description"] or "Aucune description"
            base_site_name = base_site["base_site_name"]
            del feature["properties"]["t_base_site"]

            if "year" in parameters and q_date is not None:
                for dy in DB.session.execute(q_date).all():
                    if id_site == dy[0]:
                        feature["properties"]["date_max"] = str(dy[1])
            else:
                feature["properties"]["date_max"] = str(d[1]) if d[1] else "Aucune visite"

            feature["properties"]["nom_taxon"] = str(d[2])
            feature["properties"]["nb_visit"] = str(d[3])
            feature["properties"]["organisme"] = str(d[4]) if d[4] else "Aucun"
            feature["properties"]["base_site_code"] = base_site_code
            feature["properties"]["base_site_description"] = base_site_description
            feature["properties"]["base_site_name"] = base_site_name
            features.append(feature)

        return [page_info, FeatureCollection(features)]
    return None


@blueprint.route("/transects/<id_site>", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_one_transect(id_site):
    return transect_service.build_transect_feature(
        id_site, blueprint.config["municipality_type_code"], MODULE_CODE
    )


@blueprint.route("/transects", methods=["POST"])
@permissions.check_cruved_scope("C", get_scope=True, module_code=MODULE_CODE)
@json_resp
def add_transect(scope):
    data = dict(request.get_json())
    plots = data.pop("cor_plots", [])
    sensors = data.pop("sensors", [])

    try:
        id_base_site = transect_service.create_transect_with_site(
            data, plots, sensors, MODULE_CODE, blueprint.config["site_type_code"], create_plot
        )
        DB.session.commit()
        return transect_service.build_transect_feature(
            id_base_site, blueprint.config["municipality_type_code"], MODULE_CODE
        )
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/transects/<id_transect>", methods=["PATCH"])
@permissions.check_cruved_scope("U", get_scope=True, module_code=MODULE_CODE)
@json_resp
def update_transect(id_transect, scope):
    data = dict(request.get_json())
    try:
        existing_transect = transect_service.get_transect(id_transect)
        if existing_transect is None:
            return {"error": f"Transect {id_transect} does not exist"}, 404

        digitiser = None
        if existing_transect.t_base_site and existing_transect.t_base_site.id_digitiser:
            digitiser = DB.session.get(User, existing_transect.t_base_site.id_digitiser)

        permission_service.check_user_cruved_transect(g.current_user, existing_transect, str(scope), digitiser)

        id_base_site = transect_service.update_transect_with_site(data, data.pop("cor_plots", []), create_plot)
        DB.session.commit()
        return transect_service.build_transect_feature(
            id_base_site, blueprint.config["municipality_type_code"], MODULE_CODE
        )
    except InsufficientRightsError as e:
        return {"error": str(e)}, 403
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500

@blueprint.route("/transects/<id_transect>", methods=["DELETE"])
@permissions.check_cruved_scope("D", module_code=MODULE_CODE)
@json_resp
def delete_transect(id_transect):
    try:
        transect_service.delete_transect(id_transect)
        return {"message": "Transect deleted successfully"}
    except ValueError as e:
        return {"error": str(e)}, 404
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/stations/<id_station>/transects", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_transects_by_station(id_station):
    return transect_service.list_transects_by_station_detailed(id_station)