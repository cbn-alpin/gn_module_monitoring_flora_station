CREATE SCHEMA pr_monitoring_flora_station AUTHORIZATION geonatadmin;

CREATE SEQUENCE pr_monitoring_flora_station.t_stations_id_station_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.t_transects_id_transect_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.t_temperature_sensors_id_sensor_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.t_plots_id_plot_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.t_plot_surveys_id_plot_survey_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.cor_plot_survey_strata_id_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.cor_plot_survey_substrates_id_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.cor_plot_survey_disturbances_id_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
CREATE SEQUENCE pr_monitoring_flora_station.cor_visit_disturbances_id_seq
	INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;


-- pr_monitoring_flora_station.t_stations definition

CREATE TABLE pr_monitoring_flora_station.t_stations (
	id_station serial4 NOT NULL,
	geom public.geometry(point, 4326) NULL,
	remarks text NULL,
	cd_nom int4 NOT NULL,
	"name" varchar(50) NOT NULL,
	is_managed bool NULL,
	CONSTRAINT t_stations_pkey PRIMARY KEY (id_station)
);


-- pr_monitoring_flora_station.t_transects definition

CREATE TABLE pr_monitoring_flora_station.t_transects (
	id_transect serial4 NOT NULL,
	id_base_site int4 NOT NULL,
	id_station int4 NULL,
	transect_label varchar(50) NULL,
	geom_start public.geometry(point, 4326) NULL,
	geom_end public.geometry(point, 4326) NULL,
	id_nomenclature_plot_position int4 NOT NULL,
	plot_size varchar(50) NULL,
	plot_shape text NULL,
	azimuth int4 NULL,
	CONSTRAINT pk_id_t_transects PRIMARY KEY (id_transect)
);


-- pr_monitoring_flora_station.t_temperature_sensors definition

CREATE TABLE pr_monitoring_flora_station.t_temperature_sensors (
	id_sensor serial4 NOT NULL,
	id_transect int4 NOT NULL,
	serial_number varchar(50) NOT NULL,
	install_date date NOT NULL,
	CONSTRAINT t_temperature_sensors_pkey PRIMARY KEY (id_sensor),
	CONSTRAINT unique_sensor_transect_date UNIQUE (serial_number, id_transect, install_date)
);


-- pr_monitoring_flora_station.t_plots definition

CREATE TABLE pr_monitoring_flora_station.t_plots (
	id_plot serial4 NOT NULL,
	id_transect int4 NOT NULL,
	code_plot varchar(50) NOT NULL,
	distance_plot int4 NULL,
	id_parent int4 NULL,
	CONSTRAINT pk_id_t_plots PRIMARY KEY (id_plot)
);


-- pr_monitoring_flora_station.t_plot_surveys definition

CREATE TABLE pr_monitoring_flora_station.t_plot_surveys (
	id_plot_survey serial4 NOT NULL,
	id_plot int4 NOT NULL,
	id_base_visit int4 NOT NULL,
	is_exclosure bool NULL,
	remarks text NULL,
	taxon_present bool NULL,
	flowering_stems_count int4 NULL,
	non_flowering_stems_count int4 NULL,
	CONSTRAINT pk_id_t_plot_surveys PRIMARY KEY (id_plot_survey)
);


-- pr_monitoring_flora_station.cor_plot_survey_strata definition

CREATE TABLE pr_monitoring_flora_station.cor_plot_survey_strata (
	id_plot_survey_stratum serial4 NOT NULL,
	id_plot_survey int4 NOT NULL,
	id_nomenclature_stratum int4 NOT NULL,
	cover_percentage int4 NULL,
	CONSTRAINT pk_id_cor_plot_survey_strata PRIMARY KEY (id_plot_survey_stratum)
);


-- pr_monitoring_flora_station.cor_plot_survey_substrates definition

CREATE TABLE pr_monitoring_flora_station.cor_plot_survey_substrates (
	id_plot_survey_substrate serial4 NOT NULL,
	id_plot_survey int4 NOT NULL,
	id_nomenclature_substrate int4 NOT NULL,
	cover_percentage int4 NULL,
	CONSTRAINT pk_id_cor_plot_survey_substrates PRIMARY KEY (id_plot_survey_substrate)
);


-- pr_monitoring_flora_station.cor_plot_survey_disturbances definition

CREATE TABLE pr_monitoring_flora_station.cor_plot_survey_disturbances (
	id_plot_survey_disturbance serial4 NOT NULL,
	id_plot_survey int4 NOT NULL,
	id_nomenclature_disturbance int4 NOT NULL,
	CONSTRAINT pk_id_cor_plot_survey_disturbances PRIMARY KEY (id_plot_survey_disturbance)
);


-- pr_monitoring_flora_station.cor_visit_disturbances definition

CREATE TABLE pr_monitoring_flora_station.cor_visit_disturbances (
	id_visit_disturbance serial4 NOT NULL,
	id_base_visit int4 NOT NULL,
	id_nomenclature_disturbance int4 NOT NULL,
	CONSTRAINT pk_id_cor_visit_disturbances PRIMARY KEY (id_visit_disturbance)
);


-- Foreign keys

ALTER TABLE pr_monitoring_flora_station.t_stations
	ADD CONSTRAINT fk_t_stations_cd_nom FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom) ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.t_transects
	ADD CONSTRAINT fk_t_transect_id_station FOREIGN KEY (id_station) REFERENCES pr_monitoring_flora_station.t_stations(id_station) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE pr_monitoring_flora_station.t_transects
	ADD CONSTRAINT fk_t_transects_id_base_site FOREIGN KEY (id_base_site) REFERENCES gn_monitoring.t_base_sites(id_base_site) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.t_temperature_sensors
	ADD CONSTRAINT fk_t_temperature_sensors_id_transect FOREIGN KEY (id_transect) REFERENCES pr_monitoring_flora_station.t_transects(id_transect) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.t_plots
	ADD CONSTRAINT fk_t_plots_id_parent FOREIGN KEY (id_parent) REFERENCES pr_monitoring_flora_station.t_plots(id_plot) ON DELETE CASCADE;
ALTER TABLE pr_monitoring_flora_station.t_plots
	ADD CONSTRAINT fk_t_plots_id_transect FOREIGN KEY (id_transect) REFERENCES pr_monitoring_flora_station.t_transects(id_transect) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.t_plot_surveys
	ADD CONSTRAINT fk_t_plot_surveys_id_base_visit FOREIGN KEY (id_base_visit) REFERENCES gn_monitoring.t_base_visits(id_base_visit) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE pr_monitoring_flora_station.t_plot_surveys
	ADD CONSTRAINT fk_t_plot_surveys_id_plot FOREIGN KEY (id_plot) REFERENCES pr_monitoring_flora_station.t_plots(id_plot) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.cor_plot_survey_strata
	ADD CONSTRAINT fk_cor_plot_survey_strata_id_nomenclature_stratum FOREIGN KEY (id_nomenclature_stratum) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;
ALTER TABLE pr_monitoring_flora_station.cor_plot_survey_strata
	ADD CONSTRAINT fk_cor_plot_survey_strata_id_plot_survey FOREIGN KEY (id_plot_survey) REFERENCES pr_monitoring_flora_station.t_plot_surveys(id_plot_survey) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.cor_plot_survey_substrates
	ADD CONSTRAINT fk_cor_plot_survey_substrates_id_nomenclature_substrate FOREIGN KEY (id_nomenclature_substrate) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;
ALTER TABLE pr_monitoring_flora_station.cor_plot_survey_substrates
	ADD CONSTRAINT fk_cor_plot_survey_substrates_id_plot_survey FOREIGN KEY (id_plot_survey) REFERENCES pr_monitoring_flora_station.t_plot_surveys(id_plot_survey) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.cor_plot_survey_disturbances
	ADD CONSTRAINT fk_cor_plot_survey_disturbances_id_nomenclature_disturbance FOREIGN KEY (id_nomenclature_disturbance) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE pr_monitoring_flora_station.cor_plot_survey_disturbances
	ADD CONSTRAINT fk_cor_plot_survey_disturbances_id_plot_survey FOREIGN KEY (id_plot_survey) REFERENCES pr_monitoring_flora_station.t_plot_surveys(id_plot_survey) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE pr_monitoring_flora_station.cor_visit_disturbances
	ADD CONSTRAINT fk_cor_visit_disturbances_id_base_visit FOREIGN KEY (id_base_visit) REFERENCES gn_monitoring.t_base_visits(id_base_visit) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE pr_monitoring_flora_station.cor_visit_disturbances
	ADD CONSTRAINT fk_cor_visit_disturbances_id_nomenclature_disturbance FOREIGN KEY (id_nomenclature_disturbance) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON DELETE CASCADE ON UPDATE CASCADE;