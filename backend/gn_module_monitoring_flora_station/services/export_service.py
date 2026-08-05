from ..utils.export_columns import get_base_column_name, get_pro_column_name, get_mapping_columns
from ..utils.string_utils import clean_string, strip_html


class ExportService:
    """
    Orchestration de l'export des données du module (station, visites, relevés).
    """

    def __init__(self, visit_report_repo=None):
        from ..repositories.visit_report_repository import VisitReportRepository
        self.visit_report_repo = visit_report_repo or VisitReportRepository()

    def get_base_columns(self):
        return get_base_column_name()

    def get_pro_columns(self):
        return get_pro_column_name()

    def get_columns_mapping(self):
        return get_mapping_columns()

    def build_export_filename(self, raw_name):
        return clean_string(strip_html(raw_name))

    def get_export_data(self, filters):
        return self.visit_report_repo.get_export_query(filters)

    def build_export_row(self, visit):
        mapping_columns = self.get_columns_mapping()
        row = visit.as_dict()
        row = dict(
            (mapping_columns[key], value)
            for (key, value) in row.items()
            if key in mapping_columns
        )
        row = {k: int(v) if isinstance(v, bool) else v for k, v in row.items()}
        return row

    def pivot_covers(self, row, export_format):
        if export_format != "csv":
            return row
        if row.get("covstrate"):
            for stratum, cover in row["covstrate"].items():
                row[clean_string(stratum).lower()] = cover
            row.pop("covstrate")
        if row.get("covsubstrate"):
            for substrate, cover in row["covsubstrate"].items():
                row[clean_string(substrate).lower()] = cover
            row.pop("covsubstrate")
        return row

    def get_csv_headers(self):
        column_name = self.get_base_columns()
        column_name_pro = self.get_pro_columns()
        strate_list = self.visit_report_repo.get_strate_list_for_export()
        substrate_list = self.visit_report_repo.get_substrate_list_for_export()
        return (
            column_name
            + [clean_string(x).lower() for x in strate_list]
            + [clean_string(x).lower() for x in substrate_list]
            + column_name_pro
        )