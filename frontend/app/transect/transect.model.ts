export interface ISite {
  geometry?: any;
  properties?: {
    id_base_site?: number;
    id_transect?: number;
    id_station?: number;
    cd_nom?: number;
    organisme?: string;
    nom_taxon?: string;
    nom_commune?: string;
    plot_size?: number;
    plot_shape?: string;
    cor_plots?: any[];
    plot_position?: any;
    transect_label?: string;
    base_site_code?: string;
    base_site_description?: string;
    base_site_name?: string;
    date_max?: string;
    observers?: any[];
    azimuth?: number;
    can_edit?: boolean;
    station_name?: string;
  };
}
export interface GeoPoint {
    type: string;
    coordinates: number[];
}

export interface Transect {
    id_transect: number;
    id_base_site: number;
    id_station: number;
    transect_label: string;
    geom_start: GeoPoint;
    geom_end: GeoPoint;
    nb_visits: number;
    last_visit: string;
    plot_size: string;
    plot_shape: string;
    azimuth: number;
    id_nomenclature_plot_position: number;
}