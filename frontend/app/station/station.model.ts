export interface Station {
    id_station: number;
    cd_nom: number;
    remarks: string;
    geom: any;
    taxon_name: string;
    site_gere?: boolean;
    type_gestion?: string;
}