def get_base_column_name():
    """
    Colonnes de base pour l'export (dans l'ordre d'affichage).
    """
    return [
        "identifiant_site",
        "identifiant_visite",
        "date_visite",
        "identifiant_releve",
        "code_placette",
        "en_defens",
        "remarques",
        "taxon_present",
        "tiges_fleuries",
        "tiges_non_fleuries",
        "facteurs_influence_visite",
        "facteurs_influence_placette",
        "observateurs",
        "taxon",
        "nom_transect",
        "surface_placette",
        "position_placette",
        "organisme",
    ]


def get_pro_column_name():
    """
    Colonnes réservées à l'export "pro" (avec identifiants techniques).
    """
    return ["cdnom", "covcodestrate", "covcodesubstrate"]


def get_mapping_columns():
    """
    Mapping colonne technique (colonne SQL de la vue) / libellé colonne de sortie.
    """
    return {
        "idbsite": "identifiant_site",
        "idbvisit": "identifiant_visite",
        "visitdate": "date_visite",
        "idreleve": "identifiant_releve",
        "codeplot": "code_placette",
        "isexclosure": "en_defens",
        "remarks": "remarques",
        "taxonpresent": "taxon_present",
        "floweringstems": "tiges_fleuries",
        "nonfloweringstems": "tiges_non_fleuries",
        "lbdisturbance": "facteurs_influence_visite",
        "lbplotdisturbance": "facteurs_influence_placette",
        "observers": "observateurs",
        "lbtaxon": "taxon",
        "transectlb": "nom_transect",
        "plotsize": "surface_placette",
        "plotpos": "position_placette",
        "nom_organisme": "organisme",
        "cd_nom": "cdnom",
        "covstrate": "covstrate",
        "covcodestrate": "covcodestrate",
        "covsubstrate": "covsubstrate",
        "covcodesubstrate": "covcodesubstrate",
        "geom": "points_depart_et_arrivee",
        "geom_start": "geom_start",
        "geom_end": "geom_end",
    }