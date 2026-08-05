from flask import request, send_from_directory
from werkzeug.exceptions import NotFound

from geonature.utils.env import DB, ROOT_DIR
from geonature.core.gn_permissions import decorators as permissions
from utils_flask_sqla.response import json_resp
from utils_flask_sqla_geo.utilsgeometry import FionaShapeService

from ..blueprint import blueprint
from ..services.visit_report_service import VisitReportService
from ..services.export_service import ExportService
from ..models import ExportVisits
from gn_module_monitoring_flora_station import MODULE_CODE, METADATA_CODE
import os
import datetime

from geojson import FeatureCollection
from geoalchemy2.shape import to_shape
from utils_flask_sqla.response import to_csv_resp, to_json_resp



export_service = ExportService()

visit_report_service = VisitReportService()


@blueprint.route("/sites/<id_site>/visits", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_all_visits(id_site):
    items_per_page = blueprint.config["items_per_page"]
    return visit_report_service.list_visits_by_site(id_site, items_per_page)


@blueprint.route("/visits/<id_visit>", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_one_visit(id_visit):
    return visit_report_service.build_visit_detail(id_visit)


@blueprint.route("/visits", methods=["POST"])
@permissions.check_cruved_scope("C", get_scope=True, module_code=MODULE_CODE)
@json_resp
def add_visit(scope):
    data = dict(request.get_json())
    try:
        visit = visit_report_service.create_visit(data, MODULE_CODE, METADATA_CODE)
        DB.session.commit()
        return visit.as_dict()
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/visits/<id_visit>", methods=["PATCH"])
@permissions.check_cruved_scope("U", module_code=MODULE_CODE)
@json_resp
def update_visit(id_visit):
    data = dict(request.get_json())
    try:
        visit = visit_report_service.update_visit(id_visit, data)
        DB.session.commit()
        return visit.as_dict()
    except NotFound:
        raise
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/visits/export", methods=["GET"])
@permissions.check_cruved_scope("E", module_code=MODULE_CODE)
def export_visits():
    """
    Télécharge les données d'une visite (ou des visites)
    """
    parameters = request.args
    export_format = parameters["export_format"] if "export_format" in request.args else "shapefile"

    data = export_service.get_export_data(parameters)

    output_items = []
    for d in data:
        row = export_service.build_export_row(d)

        if export_format == "csv" and d.geom:
            row["geom"] = to_shape(d.geom)

        row = export_service.pivot_covers(row, export_format)
        output_items.append(row)

    file_name = datetime.datetime.now().strftime("%Y_%m_%d_%Hh%Mm%S")

    if export_format == "csv":
        headers = export_service.get_csv_headers()
        return to_csv_resp(file_name, output_items, headers, ";")
    elif export_format == "geojson":
        features = []
        for visit in data:
            feature = visit.as_geofeature("geom", "idbsite", False)
            features.append(feature)
        geojson = FeatureCollection(features)
        return to_json_resp(
            geojson, as_file=True, filename=file_name, indent=4, extension="geojson"
        )
    else:
        dir_path = str(ROOT_DIR / "backend/static/shapefiles")
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        FionaShapeService.create_shapes_struct(
            db_cols=ExportVisits.__mapper__.c,
            srid=4326,
            dir_path=dir_path,
            file_name=file_name,
        )
        for visit in data:
            FionaShapeService.create_feature(visit.as_dict(), visit.geom)
        FionaShapeService.save_and_zip_shapefiles()
        return send_from_directory(dir_path, file_name + ".zip", as_attachment=True)