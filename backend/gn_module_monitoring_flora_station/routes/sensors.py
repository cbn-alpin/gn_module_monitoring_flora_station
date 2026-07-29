from flask import request
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from geonature.utils.env import DB
from geonature.core.gn_permissions import decorators as permissions
from utils_flask_sqla.response import json_resp

from ..blueprint import blueprint
from ..models import SfsSensor
from ..services.sensor_service import SensorService
from gn_module_monitoring_flora_station import MODULE_CODE

sensor_service = SensorService()


@blueprint.route("/sensors", methods=["POST"])
@permissions.check_cruved_scope("C", get_scope=True, module_code=MODULE_CODE)
@json_resp
def add_sensor(scope):
    data = dict(request.get_json())
    try:
        sensor = sensor_service.create_sensor(data)
        return sensor_service.build_sensor_detail(sensor.id_sensor)
    except IntegrityError as e:
        DB.session.rollback()
        if isinstance(e.orig, UniqueViolation):
            return {"error": "This sensor is already installed on a transect at this date"}, 409
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/transects/<id_transect>/sensors", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_sensors_by_transect(id_transect):
    items_per_page = blueprint.config["items_per_page"]
    return sensor_service.list_sensors_by_transect(id_transect, items_per_page)


@blueprint.route("/sensors/<id_sensor>", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_one_sensor(id_sensor):
    return sensor_service.build_sensor_detail(id_sensor)


@blueprint.route("/sensors/<id_sensor>", methods=["PATCH"])
@permissions.check_cruved_scope("U", get_scope=True, module_code=MODULE_CODE)
@json_resp
def update_sensor(id_sensor, scope):
    data = dict(request.get_json())
    try:
        sensor = SfsSensor(**data)
        sensor = sensor_service.update_sensor(sensor)
        return sensor_service.build_sensor_detail(sensor.id_sensor)
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/sensors/<id_sensor>", methods=["DELETE"])
@permissions.check_cruved_scope("D", module_code=MODULE_CODE)
@json_resp
def delete_sensor(id_sensor):
    try:
        sensor_service.delete_sensor(id_sensor)
        return {"message": "Sensor deleted successfully"}
    except ValueError as e:
        return {"error": str(e)}, 404
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500