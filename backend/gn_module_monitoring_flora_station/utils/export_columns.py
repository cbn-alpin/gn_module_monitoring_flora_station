def get_base_column_name():
    """
    Mapping colonne technique / libellé colonne pour l'export de base.
    """
    return [
        "identifiant_site",
        "label_transect",
        "date_visite",
        "identifiant_visite",
        "identifiant_releve",
        "code_placette",
        "position_placette",
        "surface_en_m2",
        "observateurs",
        "taxon",
        "points_depart_et_arrivee",
        "perturbations",
    ]


def get_pro_column_name():
    """
    Colonnes réservées à l'export "pro" (avec identifiants techniques).
    """
    return ["cdnom", "covcdnom", "covcodestrate", "covcodesubstrat"]


def get_mapping_columns():
    """
    Mapping colonne technique / libellé colonne, utilisé par l'export.
    """
    return {
        "idbsite": "identifiant_site",
        "transectlb": "label_transect",
        "visitdate": "date_visite",
        "idbvisit": "identifiant_visite",
        "idreleve": "identifiant_releve",
        "codeplot": "code_placette",
        "plotpos": "position_placette",
        "plotsize": "surface_en_m2",
        "observers": "observateurs",
        "lbtaxon": "taxon",
        "geom_start": "geom_start",
        "geom_end": "geom_end",
        "lbperturb": "perturbations",
        "cd_nom": "cdnom",
        "geom": "points_depart_et_arrivee",
        "geom_wkt": "geom_wkt",
        "covstrate": "covstrate",
        "covcodestrate": "covcodestrate",
        "covsubstrat": "covsubstrat",
        "covcodesubstrat": "covcodesubstrat",
    }