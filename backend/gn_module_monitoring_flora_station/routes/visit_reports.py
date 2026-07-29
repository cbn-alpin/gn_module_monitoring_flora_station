from flask import request
from werkzeug.exceptions import NotFound

from geonature.utils.env import DB
from geonature.core.gn_permissions import decorators as permissions
from utils_flask_sqla.response import json_resp

from ..blueprint import blueprint
from ..services.visit_report_service import VisitReportService
from gn_module_monitoring_flora_station import MODULE_CODE, METADATA_CODE

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