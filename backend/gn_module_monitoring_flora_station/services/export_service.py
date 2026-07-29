from ..utils.export_columns import get_base_column_name, get_pro_column_name, get_mapping_columns
from ..utils.string_utils import clean_string, strip_html


class ExportService:
    """
    Orchestration de l'export des données du module (station, visites, relevés).
    """

    def get_base_columns(self):
        return get_base_column_name()

    def get_pro_columns(self):
        return get_pro_column_name()

    def get_columns_mapping(self):
        return get_mapping_columns()

    def build_export_filename(self, raw_name):
        """
        Construit un nom de fichier d'export propre à partir d'un nom brut
        (station, taxon...), en nettoyant les caractères problématiques.
        """
        return clean_string(strip_html(raw_name))