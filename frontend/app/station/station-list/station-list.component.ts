import { Component, OnInit, Injectable, AfterViewInit, OnDestroy, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import {
  NgbDateParserFormatter,
  NgbDatepickerConfig,
  NgbDatepickerI18n,
  NgbDateStruct,
} from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';
import { Page } from '../../shared/models/page.model';
import { Transect } from '../../transect/transect.model';
import * as L from 'leaflet';
import 'Leaflet.Deflate';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';

import { MapService } from '@geonature_common/map/map.service';
import { MapListService } from '@geonature_common/map-list/map-list.service';
import { ConfigService } from '@geonature/services/config.service';

import { StationService } from '../station.service';
import { TransectService } from '../../transect/transect.service';
import { StoreService } from '../../shared/services/store.service';
import { UserService } from '../../core/services/user.service';
import { TaxonService } from '../../core/services/taxon.service';
import * as _ from 'lodash';


import { animate, state, style, transition, trigger } from '@angular/animations';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';


const I18N_VALUES = {
  fr: {
    weekdays: ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di'],
    months: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aou', 'Sep', 'Oct', 'Nov', 'Déc'],
  },
};

@Injectable()
export class I18n {
  language = 'fr';
}

@Injectable()
export class CustomDatepickerI18n extends NgbDatepickerI18n {
  constructor(private _i18n: I18n) {
    super();
  }
  getWeekdayLabel(weekday: number): string {
    return I18N_VALUES[this._i18n.language].weekdays[weekday - 1];
  }
  getWeekdayShortName(weekday: number): string {
    return I18N_VALUES[this._i18n.language].weekdays[weekday - 1];
  }
  getMonthShortName(month: number): string {
    return I18N_VALUES[this._i18n.language].months[month - 1];
  }
  getMonthFullName(month: number): string {
    return this.getMonthShortName(month);
  }
  getDayAriaLabel(date: NgbDateStruct): string {
    return `${date.day}-${date.month}-${date.year}`;
  }
}

@Injectable()
export class NgbDateCustomParserFormatter extends NgbDateParserFormatter {
  parse(value: string): NgbDateStruct {
    throw new Error('Method not implemented.');
  }
  format(date: NgbDateStruct): string {
    return date ? `${date.day}-${date.month}-${date.year}` : '';
  }
}

@Component({
  selector: 'station-list',
  templateUrl: 'station-list.component.html',
  styleUrls: ['station-list.component.scss'],
  providers: [
    NgbDatepickerConfig,
    I18n,
    { provide: NgbDateParserFormatter, useClass: NgbDateCustomParserFormatter },
    { provide: NgbDatepickerI18n, useClass: CustomDatepickerI18n },
  ],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({ height: '0px', minHeight: '0' })),
      state('expanded', style({ height: '*' })),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
})
export class StationListComponent implements OnInit, AfterViewInit, OnDestroy {
  public sites;
  public filteredData = [];
  public addIsAllowed: boolean = false;
  public dataLoaded = false;
  private modalRef: NgbModalRef;
  public center;
  public zoom;
  private _map;
  private _deflate_features;
  public filterForm: FormGroup;
  public page = new Page();
  minDate: any;
  maxDate: any;
  public stations = [];
  public expandedStations: { [key: number]: Transect[] } = {};
  public dataSource = new MatTableDataSource([]);
  public columnsToDisplay = ['Station', 'Taxon', 'Nbre transect', 'Nbre visite', 'Dernière visite'];
  public columnsToDisplayWithExpand = [...this.columnsToDisplay, 'expand'];
  public expandedElement: any;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  public tabYear = [];
  public tabArea = [];
  public tabOrganism = [];
  public tabTaxon=[];
  public taxons: any[] = [];
  private transectLayers: L.Layer[] = [];
  private selectedTransectLayer: L.Polyline = null;
  private transectLayerMap: Map<number, L.Polyline> = new Map();
  private selectedTransectId: number = null;
  public formEditStation: FormGroup;
  private stationToEdit: any = null;
  public taxonCodeControl = new FormControl();
  public taxonFormatter = (taxon: any) => {
    return taxon?.nom_complet ? taxon.nom_complet : '';
  };
  private stationToDelete: any = null;
  private confirmModalRef: NgbModalRef;
  public columnTooltips: { [key: string]: string } = {
    'Station': 'Nom de la station',
    'Taxon': 'Taxon suivi sur la station',
    'Nbre transect': 'Nombre de transects de la station',
    'Nbre visite': 'Nombre de visites de la station',
    'Dernière visite': 'Date de la dernière visite',
  };
  public transectColumnTooltips: { [key: string]: string } = {
    'Nom transect': 'Nom du transect',
    'Nbre visite': 'Nombre de visites du transect',
    'Dernière visite': 'Date de la dernière visite du transect',
  };

  constructor(
    private config: ConfigService,
    public mapService: MapService,
    private _stationApi: StationService,
    private _transectApi: TransectService,
    private userService: UserService,
    public dateParser: NgbDateParserFormatter,
    datePickerConfig: NgbDatepickerConfig,
    public storeService: StoreService,
    public mapListService: MapListService,
    public taxonService: TaxonService,
    public router: Router,
    private toastr: ToastrService,
    private formBuilder: FormBuilder,
    private modalService: NgbModal,
  ) {
    datePickerConfig.outsideDays = 'hidden';
    datePickerConfig.minDate = { year: 1735, month: 1, day: 1 };
    datePickerConfig.maxDate = { year: 2200, month: 1, day: 1 };
  }

  ngOnInit() {
    this.storeService.loadQueryString();
    this.checkPermission();

    this.center = this.storeService.sfsConfig.zoom_center;
    this.zoom = this.storeService.sfsConfig.zoom;
    const savedPageSize = localStorage.getItem('sfs-page-size');
    this.page.size = savedPageSize ? parseInt(savedPageSize, 10) : this.storeService.sfsConfig.items_per_page;
    this.initFilters();
    this.getStations(this.getFiltersFromQueryString());
  }

  private getFiltersFromQueryString() {
    let filter: any = {};
    this.storeService.queryString.keys().forEach(key => {
      filter[key] = this.storeService.queryString.get(key);
    });
    return Object.keys(filter).length > 0 ? filter : undefined;
  }

  ngAfterViewInit() {
    let moduleCode = this.config['MFS']['MODULE_CODE'].toLocaleLowerCase();
    this._map = this.mapService.getMap();
    this._deflate_features = (L as any).deflate({
      minSize: 10,
      markerOptions: () => {
        return {
          icon: new L.Icon({
            iconUrl: `./assets/${moduleCode}/assets/marker-icon.png`,
            shadowUrl: `./assets/${moduleCode}/assets/marker-shadow.png`,
            iconSize: [25, 41],
            iconAnchor: [13, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          })
        };
      }
    });
    this._deflate_features.addTo(this._map);
    this._map.on('zoomend', () => {
      const zoom = this._map.getZoom();

      if (zoom >= 12) {
        Object.values(this.mapListService.layerDict).forEach((marker: any) => {
          marker.setOpacity(0);
        });

        this.filteredData.forEach(station => {
          if (!this.expandedStations[station.id_station]) {
            this._stationApi.getTransectsByStation(station.id_station).subscribe(
              (data: any[]) => {
                this.expandedStations[station.id_station] = data;
                data.forEach(transect => {
                  let line = L.polyline(
                    [[transect.geom_start.coordinates[1], transect.geom_start.coordinates[0]],
                    [transect.geom_end.coordinates[1], transect.geom_end.coordinates[0]]],
                    { color: '#3388ff' }
                  )
                    .bindTooltip(transect.transect_label)
                    .addTo(this._map);
                  this.transectLayerMap.set(transect.id_transect, line);
                  this.transectLayers.push(line);
                });
              }
            );
          }
        });
      } else {
        Object.values(this.mapListService.layerDict).forEach((marker: any) => {
          marker.setOpacity(1);
        });

        this.transectLayers.forEach(layer => this._map.removeLayer(layer));
        this.transectLayers = [];
        this.transectLayerMap.clear();
      }
    });

    this.addCustomControl();
    this.addLegend();
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
    this._stationApi.getStationsYears().subscribe(
      (data: any[]) => {
        this.tabYear = data;
      }
    );
    this._stationApi.getStationsArea().subscribe(
      (data: any[]) => {
        this.tabArea = data;
      }
    );
    this._stationApi.getOrganism().subscribe(
      (data: any[]) => {
        this.tabOrganism = data;
      }
    );
    this._stationApi.getStationsTaxa().subscribe(
      (data: any[]) => {
        this.tabTaxon = data;
      }
    );
  }

  checkPermission() {
    this.userService.check_user_cruved_visit('C').subscribe(ucruved => {
      this.addIsAllowed = ucruved;
    });
  }

  getStations(params?: any) {
    this.dataLoaded = false;
    this._stationApi.getAllStations(params).subscribe(
      data => {
        if (data !== null) {
          if (this._deflate_features) {
            this._deflate_features.clearLayers();
          }
          this.mapListService.layerDict = {};
          this.sites = data[1];
          this.page.totalElements = data[0].totalItems;
          if (this.storeService.sfsConfig.pagination_serverside) {
            this.page.size = data[0].itemsPerPage;
          }

          this.filteredData = data[1].features.map(feature => {
            this._stationApi.getTransectsByStation(feature.properties.id_station).subscribe(
              (transects: Transect[]) => {
                this.expandedStations[feature.properties.id_station] = transects;
              }
            );
            return {
              'Station': feature.properties.name !== "" ? feature.properties.name : "Sans nom",
              'Taxon': feature.properties.taxon_name,
              'Nbre visite': feature.properties.nb_visits,
              'Nbre transect': feature.properties.nb_transect,
              'Dernière visite': feature.properties.last_visit,
              'id_station': feature.properties.id_station
            };
          });

          this.dataSource.data = this.filteredData;
          this.page.totalElements = data[0].totalItems;
        } else {
          if (this._deflate_features) {
            this._deflate_features.clearLayers();
          }
          this.mapListService.layerDict = {};
          this.filteredData = [];
          this.dataSource.data = [];
        }
        this.dataLoaded = true;
      },
      error => {
        let msg = 'Une erreur est survenue lors de la récupération des informations sur le serveur.';
        if (error.status == 404) {
          this.page.totalElements = 0;
          this.page.size = 0;
          this.filteredData = [];
        } else if (error.status == 403) {
          msg = "Vous n'êtes pas autorisé à afficher ces données.";
        } else {
          this.toastr.error(msg, '', { positionClass: 'toast-top-right' });
        }
        this.dataLoaded = true;
      }
    );
}

  onViewStation(id_station: number) {
    this.transectLayers.forEach(layer => this._map.removeLayer(layer));
    this.transectLayers = [];
    this.transectLayerMap.clear();
    this.selectedTransectLayer = null;

    const data: Transect[] = this.expandedStations[id_station];
    if (data) {
      data.forEach((transect: Transect) => {
        if (!transect.geom_start || !transect.geom_end) return;
        let line = L.polyline(
          [[transect.geom_start.coordinates[1], transect.geom_start.coordinates[0]],
          [transect.geom_end.coordinates[1], transect.geom_end.coordinates[0]]],
          { color: '#3388ff' }
        )
          .bindTooltip(transect.transect_label)
          .addTo(this._map);
        line.on('click', () => {
          this.onTransectMapClick(transect.id_transect, transect.id_station);
        });
        line.on('mouseover', () => {
          this._map.getContainer().style.cursor = 'cell';
        });
        line.on('mouseout', () => {
          this._map.getContainer().style.cursor = '';
        });
        this.transectLayerMap.set(transect.id_transect, line);
        this.transectLayers.push(line);
      });

      if (this.transectLayers.length > 0) {
        let group = L.featureGroup(this.transectLayers);
        this._map.fitBounds(group.getBounds());
      }
    }
  }

  onInfo(id_base_site: any) {
    this.router.navigate([`${this.config['MFS']['MODULE_URL']}/transects`, id_base_site]);
  }

  initFilters() {
    this.filterForm = this.formBuilder.group({
      date_low: null,
      date_up: null,
      filterTaxon: this.storeService.queryString.get('filterTaxon')
        ? Number(this.storeService.queryString.get('filterTaxon'))
        : null,
      year: this.storeService.queryString.get('year'),
      area_name: this.storeService.queryString.get('area_name'),
      organism: this.storeService.queryString.get('organism'),
    });

    this.filterForm.valueChanges.subscribe(() => {
      this.onFilter();
    });

    this.filterForm.controls['date_low'].statusChanges.subscribe(() => {
      if (this.filterForm.controls['date_low'].value) {
        this.minDate = this.filterForm.controls['date_low'].value;
        if (!this.filterForm.controls['date_up'].value)
          this.filterForm.controls['date_up'].setValue(this.minDate);
      }
    });
    this.filterForm.controls['date_up'].statusChanges.subscribe(() => {
      if (this.filterForm.controls['date_up'].value) {
        this.maxDate = this.filterForm.controls['date_up'].value;
        if (!this.filterForm.controls['date_low'].value)
          this.filterForm.controls['date_low'].setValue(this.minDate);
      }
    });
  }

  setPage(pageInfo) {
    this.page.pageNumber = pageInfo.offset + 1;
    if (this.storeService.sfsConfig.pagination_serverside) {
      this.onSetParams('page', pageInfo.offset + 1);
      this.getStations(this.storeService.queryString.toString());
    }
  }

  onEachFeature(feature, layer) {
    let site = feature.properties;

    let marker = L.marker(layer.getLatLng(), {
      icon: new L.Icon({
        iconUrl: './marker-icon.png',
        shadowUrl: './marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [13, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
      })
    });

    this.mapListService.layerDict[feature.id] = marker;

    marker.bindPopup('<div class="title">' + site.name + '</div>');
    marker.bindTooltip(site.name);

    marker.on({
      click: e => {
        this.onMapClick(feature.id);
      }
    });

    marker.addTo(this._map);
  }

  onMapClick(id: string): void {
    const id_station = parseInt(id);
    const index = this.filteredData.findIndex(s => s.id_station === id_station);
    if (index === -1) {
      return;
    }
    const pageSize = this.paginator.pageSize;
    const pageIndex = Math.floor(index / pageSize);

    this.paginator.pageIndex = pageIndex;
    this.paginator.page.emit({
      pageIndex: pageIndex,
      pageSize: pageSize,
      length: this.paginator.length
    });

    const element = this.filteredData[index];
    this.expandedElement = element;
    this.onViewStation(id_station);
  }

  onRowSelect(element: any) {
    const id_station = element.id_station;
    const marker = this.mapListService.layerDict[id_station];
    if (marker) {
      this._map.removeLayer(marker);
    }

    this.onViewStation(id_station);
    setTimeout(() => {
      if (this.transectLayers.length > 0) {
        let group = L.featureGroup(this.transectLayers);
        this._map.fitBounds(group.getBounds());
      }
    }, 500);
  }

  zoomOnSelectedLayer(map, layer, zoom) {
    let latlng;
    if (layer instanceof L.Polygon || layer instanceof L.Polyline) {
      latlng = (layer as any).getCenter();
      map.setView(latlng, zoom);
    } else {
      latlng = layer._latlng;
    }
  }

  addCustomControl() {
    let initzoomcontrol = new L.Control();
    initzoomcontrol.setPosition('topleft');
    initzoomcontrol.onAdd = () => {
      var container = L.DomUtil.create(
        'button',
        ' btn btn-sm btn-outline-shadow leaflet-bar leaflet-control leaflet-control-custom'
      );
      container.innerHTML =
        '<i class="material-icons" style="vertical-align: text-bottom">crop_free</i>';
      container.style.padding = '4px 4px 1px';
      container.title = "Réinitialiser l'emprise de la carte";
      container.onclick = () => {
        this._map.setView(this.center, this.zoom);
      };
      return container;
    };
    initzoomcontrol.addTo(this._map);
  }

  onSetParams(param: string, value) {
    this.storeService.queryString = this.storeService.queryString.set(param, value);
  }

  onFilter() {
    let filter = _.clone(this.filterForm.value);
    filter.date_low = this.dateParser.format(this.filterForm.value.date_low);
    filter.date_up = this.dateParser.format(this.filterForm.value.date_up);
    filter.year = this.filterForm.value.year;
    filter.area_name = this.filterForm.value.area_name;
    filter.organism = this.filterForm.value.organism;
    filter.filterTaxon = this.filterForm.value.filterTaxon;
    Object.keys(filter).forEach(key => {
      if (filter[key]) {
        this.storeService.queryString = this.storeService.queryString.set(key, filter[key]);
      } else {
        this.storeService.queryString = this.storeService.queryString.delete(key);
      }
    });
    this.storeService.saveQueryString();
    this.getStations(filter);
  }

  resetFilters() {
    this.filterForm.reset();
    this.storeService.clearQueryString(),
      this.storeService.saveQueryString(),
      this.getStations();
    this.resetMinMaxDate();
    setTimeout(() => {
      this._map.setView(this.center, this.zoom);
    }, 100);
  }

  onNewTransect() {
    this.router.navigate([`${this.config['MFS']['MODULE_URL']}/transects/new_transect`]);
  }

  closeFix(event, datePicker) {
    if (event.target.offsetParent == null) datePicker.close();
    else if (event.target.offsetParent.nodeName != 'NGB-DATEPICKER') datePicker.close();
  }

  resetMinMaxDate() {
    this.maxDate = { year: 2200, month: 1, day: 1 };
    this.minDate = null;
  }

  onSelectTransect(id_transect: number) {
    this.transectLayers.forEach((layer: any) => {
      layer.setStyle({ color: '#3388ff' });
    });

    const selectedLayer = this.transectLayerMap.get(id_transect);
    if (selectedLayer) {
      selectedLayer.setStyle({ color: '#ff0000' });
      this.selectedTransectLayer = selectedLayer;
      this.selectedTransectId = id_transect;
    }
  }

  onTransectMapClick(id_transect: number, id_station: number) {
    const index = this.filteredData.findIndex(s => s.id_station === id_station);
    if (index === -1) {
      return;
    }
    const pageSize = this.paginator.pageSize;
    const pageIndex = Math.floor(index / pageSize);
    this.paginator.pageIndex = pageIndex;
    this.paginator.page.emit({
      pageIndex: pageIndex,
      pageSize: pageSize,
      length: this.paginator.length
    });

    const element = this.filteredData[index];
    this.expandedElement = null;
    setTimeout(() => {
      this.expandedElement = element;
      this.selectedTransectId = id_transect;
      this.onSelectTransect(id_transect);
    });
  }

  addLegend() {
    let legend = new L.Control({ position: 'bottomright' });
    legend.onAdd = () => {
      return this.storeService.buildMapLegend();
    };
    legend.addTo(this._map);
  }

  onPageChange(event: any) {
    this.page.size = event.pageSize;
    localStorage.setItem('sfs-page-size', event.pageSize.toString());
  }

  onEditStation(station: any, content: any) {
      this.stationToEdit = station;
      this._stationApi.getOneStation(station.id_station).subscribe(
        (data: any) => {
          this.formEditStation = this.formBuilder.group({
            name: [data.properties.name, Validators.required],
            remarks: [data.properties.remarks],
            cd_nom: [data.properties.cd_nom, Validators.required],
          });
          this.taxonCodeControl.setValue({
            cd_nom: data.properties.cd_nom,
            nom_complet: data.properties.taxon_name,
            nom_complet_html: data.properties.taxon_name,
          });
          this.modalRef = this.modalService.open(content, { centered: true });
        }
      );
  }
  addNewTaxonEdit(event: any) {
    this.formEditStation.patchValue({ cd_nom: event.item.cd_nom });
  }

  onSaveEditStation() {
    let station = this.formEditStation.value;
    station.id_station = this.stationToEdit.id_station;
    this._stationApi.updateStation(station).subscribe(
      data => {
        this.modalRef.close();
        this.getStations(this.getFiltersFromQueryString());
        this.toastr.success('Station modifiée avec succès', '', { positionClass: 'toast-top-right' });
      },
      error => {
        this.toastr.error('Erreur lors de la modification de la station', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  onDeleteStation(element: any, content: any) {
    if (element['Nbre transect'] > 0) {
      this.toastr.error('Cette station ne peut être supprimée car elle possède des transects', '', { positionClass: 'toast-top-rigth' });
    } else if (element['Nbre transect'] === 0) {
      this.stationToDelete = element;
      this.confirmModalRef = this.modalService.open(content, { centered: true });
    }
  }

  onConfirmDeleteStation() {
    this._stationApi.deleteStation(this.stationToDelete.id_station).subscribe(
      data => {
        this.getStations(this.getFiltersFromQueryString());
        this.confirmModalRef.close();
        this.toastr.success('Station supprimée', '', { positionClass: 'toast-top-right' });
      },
      error => {
        this.toastr.error('Erreur lors de la suppression de la station', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  ngOnDestroy() {
    this.storeService.saveQueryString();
    this.storeService.clearQueryString();
  }
}