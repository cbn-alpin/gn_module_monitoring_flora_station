from flask import request
from werkzeug.exceptions import NotFound

from geonature.utils.env import DB
from geonature.core.gn_permissions import decorators as permissions
from utils_flask_sqla.response import json_resp

from ..blueprint import blueprint
from ..models import SfsPlot
from ..services.plot_service import PlotService
from gn_module_monitoring_flora_station import MODULE_CODE

plot_service = PlotService()


def create_plot(plot_data):
    return plot_service.create_plot(plot_data, blueprint.config["max_plot_depth"])


@blueprint.route("/transects/<id_transect>/plots", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_plot_by_transect(id_transect):
    data = plot_service.list_plots_by_transect(id_transect)
    return plot_service.build_hierarchy(data)


@blueprint.route("/plots", methods=["POST"])
@permissions.check_cruved_scope("C", get_scope=True, module_code=MODULE_CODE)
@json_resp
def add_plot(scope):
    data = dict(request.get_json())
    try:
        plot = create_plot(data)
        DB.session.commit()
        return plot.as_dict()
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/plots/<id_plot>", methods=["GET"])
@permissions.check_cruved_scope("R", module_code=MODULE_CODE)
@json_resp
def get_one_plot(id_plot):
    plot = plot_service.get_plot(id_plot)
    if plot is None:
        raise NotFound(f"Plot {id_plot} does not exist")

    all_plots = plot_service.list_plots_by_transect(plot.id_transect)
    plot_dict = plot.as_dict()
    plot_dict["sub_plots"] = plot_service.build_hierarchy(all_plots, parent_id=plot.id_plot)
    return plot_dict


@blueprint.route("/plots/<id_plot>", methods=["PATCH"])
@permissions.check_cruved_scope("U", get_scope=True, module_code=MODULE_CODE)
@json_resp
def update_plot(id_plot, scope):
    data = dict(request.get_json())
    try:
        plot = SfsPlot(**data)
        plot = plot_service.update_plot(plot)
        return plot.as_dict()
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500


@blueprint.route("/plots/<id_plot>", methods=["DELETE"])
@permissions.check_cruved_scope("D", module_code=MODULE_CODE)
@json_resp
def delete_plot(id_plot):
    try:
        plot_service.delete_plot(id_plot)
        return {"message": "Plot deleted successfully"}
    except ValueError as e:
        return {"error": str(e)}, 404
    except Exception as e:
        DB.session.rollback()
        return {"error": str(e)}, 500