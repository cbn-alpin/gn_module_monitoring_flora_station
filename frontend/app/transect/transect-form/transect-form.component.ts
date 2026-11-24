import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { ToastrService } from 'ngx-toastr';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { forkJoin } from 'rxjs';
import * as _ from 'lodash';
import { FlatTreeControl } from '@angular/cdk/tree';
import { MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import { PlotNode, FlatPlotNode } from '../../plot/plot-node.model';

import { DataFormService } from '@geonature_common/form/data-form.service';
import { MapListService } from '@geonature_common/map-list/map-list.service';
import { ConfigService } from '@geonature/services/config.service';

import { TransectService } from '../transect.service';
import { StationService } from '../../station/station.service';
import { PlotService } from '../../plot/plot.service';
import { SensorService } from '../../sensor/sensor.service';
import { StoreService } from '../../shared/services/store.service';
import { UserService } from '../../core/services/user.service';
import { ISite } from '../transect.model';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs/observable/of';
import { TaxonService } from '../../core/services/taxon.service';
import { Page } from '../../shared/models/page.model';
import { VisitReportService } from '../../visit-report/visit-report.service';
@Component({
  selector: 'transect-form',
  templateUrl: 'transect-form.component.html',
  styleUrls: ['./transect-form.component.scss'],
})
export class TransectFormComponent implements OnInit, OnDestroy {
  public selectedStation: any = null;
  public currentSite: ISite;
  public sites;
  public stations = [];
  plots = [];
  transect_title: string = 'Consultation du transect ';
  public show = true;
  public idSite;
  public disabledForm = true;
  public upIsAllowed = false;
  addIsAllowed = false;
  dataLoaded = false;
  formTransect: FormGroup;
  formSensor: FormGroup;
  edit_btn: string = 'Editer';
  public rows = [];
  public page = new Page();
  public addVisitIsAllowed: boolean = false;
  taxons: any[] = [];
  isNew: boolean;
  plot_position: any;
  formPlot: FormGroup;
  private modalRef: NgbModalRef;
  public sensors = [];
  public sensorToDeleteIndex: number = null;
  sensorToDelete: number = null;
  private confirmModalRef: NgbModalRef;
  public sensorToEdit: number = null;
  public sensorToEditIndex: number = null;
  public plotHierarchy = [];
  public expandedPlots: { [key: number]: boolean } = {};
  public subplots = [];
  plotToDelete: number = null;
  plotToDeleteIndex: number = null;
  private confirmPlotModalRef: NgbModalRef;
  plotToEdit: any = null;
  plotToEditIndex: number = null;
  formStation: FormGroup;
  public taxonCodeControl = new FormControl();
  formEditPlot: FormGroup;
  formEditStation: FormGroup;
  private plotIdCounter: number = 0;
  public stationToDelete: any;
  public stationToEdit: any;
  plotToDeleteObject: any = null;
  selectedStationTransects: any[] = [];

  private _transformer = (node: PlotNode, level: number): FlatPlotNode => ({
    expandable: !!node.sub_plots && node.sub_plots.length > 0,
    id_plot: node.id_plot,
    code_plot: node.code_plot,
    distance_plot: node.distance_plot,
    level: level,
  });

  treeControl = new FlatTreeControl<FlatPlotNode>(
    node => node.level,
    node => node.expandable
  );

  treeFlattener = new MatTreeFlattener(
    this._transformer,
    node => node.level,
    node => node.expandable,
    node => node.sub_plots
  );

  plotDataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

  hasChild = (_: number, node: FlatPlotNode) => node.expandable;

  constructor(
    private config: ConfigService,
    public storeService: StoreService,
    public taxonService: TaxonService,
    private transectApi: TransectService,
    private visitReportApi: VisitReportService,
    private stationApi: StationService,
    private plotApi: PlotService,
    private sensorApi: SensorService,
    public activatedRoute: ActivatedRoute,
    private toastr: ToastrService,
    public mapListService: MapListService,
    private modalService: NgbModal,
    public router: Router,
    private userService: UserService,
    private nomenclatureServ: DataFormService,
    private formBuilder: FormBuilder
  ) {}

  ngOnInit() {
    this.idSite = this.activatedRoute.snapshot.params['idSite'];
    this.page.size = this.storeService.sfsConfig.items_per_page;
    this.isNew = !this.idSite;
    this.storeService.queryString = this.storeService.queryString.set('id_base_site', this.idSite);
    this.checkPermission();

    forkJoin([
      this.transectApi.getAllSites({ id_base_site: this.idSite }).pipe(
        catchError(error => {
          if (error.error?.message === 'sites_not_found' || error.status === 404) {
            return of(null);
          }
          throw error;
        })
      ),
      this.nomenclatureServ.getNomenclature('POSITION_PLACETTE', null, null, null, {
        orderby: 'label_default',
      }),
      this.stationApi.getAllStations(),
    ]).subscribe(
      results => {
        this.sites = results[0];
        this.plot_position = results[1] ? results[1].values : [];
        this.stations = results[2] ? results[2][1].features : [];
        this.formTransect = this.initFormTransect();
        if (!this.isNew) {
          this.loadTransect();
        } else {
          this.transect_title = 'Nouveau transect';
          this.dataLoaded = true;
          this.disabledForm = false;
        }
      },
      error => {
        this.toastr.error(
          'Une erreur est survenue lors de la récupération des informations sur le serveur.',
          '', { positionClass: 'toast-top-right' }
        );
        this.router.navigate([`${this.config['MFS']['MODULE_URL']}/`]);
      }
    );
  }

  checkPermission() {
    this.userService.check_user_cruved('U').subscribe(ucruved => {
      this.upIsAllowed = ucruved;
    });
    this.userService.check_user_cruved('C').subscribe(ucruved => {
      this.addIsAllowed = ucruved;
    });
    this.userService.check_user_cruved_visit('C').subscribe(ucruved => {
      this.addVisitIsAllowed = ucruved;
    });
  }

  initFormTransect(): FormGroup {
    return this.formBuilder.group({
      id_base_site: [null],
      base_site_description: [null],
      id_transect: [null],
      geom_end_lat: [null, Validators.required],
      geom_end_long: [null, Validators.required],
      geom_start_lat: [null, Validators.required],
      geom_start_long: [null, Validators.required],
      plot_size: [null, Validators.required],
      plot_shape: [null],
      transect_label: [null, Validators.required],
      id_station: [null],
      id_nomenclature_plot_position: [null, Validators.required],
      azimuth: [null],
    });
  }

  private loadTransect() {
    this.transectApi.getOneTransect(this.idSite).subscribe(
      site => {
        this.currentSite = site;
        if (!this.currentSite.properties?.cor_plots) {
          this.toastr.error(
            'Ajouter des placettes à votre transect.',
            '',
            { positionClass: 'toast-top-right' }
          );
        } else {
          this.plots = _.cloneDeep(this.currentSite.properties.cor_plots);
        }
        this.transect_title = this.transect_title + this.currentSite.properties?.transect_label;
        this.storeService.setCurrentSite(this.currentSite);
        this.getSensors();
        this.getPlots();
        this.getVisits();
        this.pachForm();
        this.dataLoaded = true;
      },
      error => {
        let msg = '';
        if (error.status == 403) {
          msg = "Vous n'êtes pas autorisé à afficher ces données.";
        } else {
          msg = 'Une erreur est survenue lors de la récupération des informations sur le serveur.';
        }
        this.toastr.error(msg, '', { positionClass: 'toast-top-right' });
      }
    );
  }

  pachForm() {
    this.formTransect.patchValue({
      id_base_site: this.currentSite.properties.id_base_site,
      base_site_description: this.currentSite.properties.base_site_description,
      id_transect: this.currentSite.properties.id_transect,
      geom_start_lat: this.currentSite.geometry.coordinates[0][1],
      geom_start_long: this.currentSite.geometry.coordinates[0][0],
      geom_end_lat: this.currentSite.geometry.coordinates[1][1],
      geom_end_long: this.currentSite.geometry.coordinates[1][0],
      id_nomenclature_plot_position: this.currentSite.properties.plot_position.id_nomenclature,
      plot_size: this.currentSite.properties.plot_size,
      plot_shape: this.currentSite.properties.plot_shape,
      transect_label: this.currentSite.properties.transect_label,
      azimuth: this.currentSite.properties.azimuth,
      id_station: this.currentSite.properties.id_station,
    });
    if (this.currentSite.properties?.id_station) {
      this.stationApi.getOneStation(this.currentSite.properties.id_station).subscribe(
        (data: any) => {
          this.selectedStation = data;
        }
      );
    }
  }

  backToSites() {
    this.router.navigate([`${this.config['MFS']['MODULE_URL']}/`]);
  }

  onAddPlot(content) {
    this.subplots = [];
    this.formPlot = this.formBuilder.group({
      code_plot: [null, Validators.required],
      distance_plot: [null, Validators.required],
      id_parent: [null],
    });
    this.formPlot.controls['id_parent'].valueChanges.subscribe(value => {
      if (value !== null && value !== undefined) {
        this.formPlot.controls['distance_plot'].clearValidators();
      } else {
        this.formPlot.controls['distance_plot'].setValidators(Validators.required);
      }
      this.formPlot.controls['distance_plot'].updateValueAndValidity();
    });
    this.modalRef = this.modalService.open(content, { centered: true });
  }

  findPlotById(plots: any[], id: number): any {
    for (let plot of plots) {
      if (plot.temp_id === id) {
        return plot;
      }
      if (plot.sub_plots?.length > 0) {
        const found = this.findPlotById(plot.sub_plots, id);
        if (found) return found;
      }
    }
    return null;
  }

  onSavePlot() {
    let plot = this.formPlot.value;

    if (this.isNew) {
      plot.temp_id = this.plotIdCounter++;
      plot.sub_plots = [];
      if (plot.id_parent !== null && plot.id_parent !== undefined) {
        const parent = this.findPlotById(this.plotHierarchy, plot.id_parent);
        if (parent) {
          if (!parent.sub_plots) parent.sub_plots = [];
          parent.sub_plots.push(plot);
        }
      } else {
        this.plotHierarchy.push(plot);
      }
      this.plotHierarchy = [...this.plotHierarchy];
      this.modalRef.close();
      this.toastr.success('Placette ajoutée avec succès', '', { positionClass: 'toast-top-right' });
    } else {
      plot.id_transect = this.currentSite.properties?.id_transect;
      this.plotApi.addPlot(plot).subscribe(
        data => {
          this.getPlots();
          this.modalRef.close();
          this.formTransect.markAsDirty(); 
          this.toastr.success('Placette ajoutée avec succès', '', { positionClass: 'toast-top-right' });
        },
        error => {
          this.toastr.error("Erreur lors de l'ajout de la placette", '', { positionClass: 'toast-top-right' });
        }
      );
    }
  }

  onSaveAndContinuePlot(codeInput?: HTMLInputElement) {
    let plot = this.formPlot.value;
    let savedParent = plot.id_parent;

    if (this.isNew) {
      plot.temp_id = this.plotIdCounter++;
      plot.sub_plots = [];

      if (plot.id_parent !== null && plot.id_parent !== undefined) {
        const parent = this.findPlotById(this.plotHierarchy, plot.id_parent);
        if (parent) {
          if (!parent.sub_plots) parent.sub_plots = [];
          parent.sub_plots.push(plot);
        }
      } else {
        this.plotHierarchy.push(plot);
      }
      this.plotHierarchy = [...this.plotHierarchy];

      this.formPlot.patchValue({ code_plot: null, distance_plot: null, id_parent: savedParent });
      this.formPlot.markAsPristine();
      this.toastr.success('Placette ajoutée avec succès', '', { positionClass: 'toast-top-right' });
      if (codeInput) {
        codeInput.focus();
      }
    } else {
      plot.id_transect = this.currentSite.properties?.id_transect;
      this.plotApi.addPlot(plot).subscribe(
        data => {
          this.getPlots();
          this.formPlot.patchValue({ code_plot: null, distance_plot: null, id_parent: savedParent });
          this.formPlot.markAsPristine();
          this.formTransect.markAsDirty();
          this.toastr.success('Placette ajoutée avec succès', '', { positionClass: 'toast-top-right' });
          if (codeInput) {
            codeInput.focus();
          }
        },
        error => {
          this.toastr.error("Erreur lors de l'ajout de la placette", '', { positionClass: 'toast-top-right' });
        }
      );
    }
}

  onEdit() {
    this.disabledForm = !this.disabledForm;
    if (!this.disabledForm) {
      this.edit_btn = 'Annuler';
    } else {
      this.plots = this.currentSite.properties.cor_plots;
      this.pachForm();
      this.edit_btn = 'Éditer';
    }
  }

  onSubmitTransect() {
    let transect = this.formTransect.value;
    transect.cor_plots = this.isNew ? this.plotHierarchy : this.plots;

    transect.geom_start = `SRID=4326;POINT(${transect.geom_start_long} ${transect.geom_start_lat})`;
    transect.geom_end = `SRID=4326;POINT(${transect.geom_end_long} ${transect.geom_end_lat})`;
    delete transect.geom_end_long;
    delete transect.geom_start_long;
    delete transect.geom_end_lat;
    delete transect.geom_start_lat;

    if (this.isNew) {
      transect.sensors = this.sensors;
      this.transectApi.addTransect(transect).subscribe(
        data => {
          this.toastr.success('Le transect a été ajouté avec succès', '', { positionClass: 'toast-top-right' });
          this.router.navigate([`${this.config['MFS']['MODULE_URL']}/transects`, (data as any).properties.id_base_site]);
        },
        error => {
          this.toastr.error('Une erreur est survenue lors de la création du transect', '', { positionClass: 'toast-top-right' });
          this.backToSites();
        }
      );
    } else {
      this.transectApi.updateTransect(transect).subscribe(
        data => {
          this.toastr.success('Le transect a été modifié avec succès', '', { positionClass: 'toast-top-right' });
          this.currentSite = data;
          this.storeService.setCurrentSite(this.currentSite);
          this.pachForm();
          this.plots = this.currentSite.properties.cor_plots || [];
          this.disabledForm = true;
          this.edit_btn = 'Éditer';
        },
        error => {
          this.toastr.error('Une erreur est survenue lors de la modification du transect', '', { positionClass: 'toast-top-right' });
          this.backToSites();
        }
      );
    }
  }

  getSensors() {
    this.sensorApi.getSensorsByTransect(this.currentSite.properties?.id_transect).subscribe(
      data => {
        this.sensors = data[1].sort(
          (a, b) => new Date(b.install_date).getTime() - new Date(a.install_date).getTime()
        );
      },
      error => {
        this.toastr.error('Une erreur est survenue lors de la récupération des capteurs', '', { positionClass: 'toast-top-right' });
      }
    );
  }
  getVisits() {
  this.visitReportApi.getAllVisits(this.idSite).subscribe(
    (data: any) => {
      if (data) {
        this.page.totalElements = data[0].totalItems;
        let visits = data[1] ? data[1] : [];
        visits.forEach(visit => {
          if (visit && visit.observers) {
            let fullName = '';
            let count = visit.observers.length;
            visit.observers.forEach((obs, index) => {
              if (count > 1) {
                if (index + 1 == count) {
                  fullName += obs.nom_role + ' ' + obs.prenom_role;
                } else {
                  fullName += obs.nom_role + ' ' + obs.prenom_role + ', ';
                }
              } else {
                fullName = obs.nom_role + ' ' + obs.prenom_role;
              }
            });
            visit.observers = fullName;
          }
        });
        this.rows = visits;
      } else {
        this.rows = [];
      }
    },
    error => {
      this.toastr.error('Erreur lors de la récupération des visites', '', { positionClass: 'toast-top-right' });
    }
  );
}

  onNewVisit() {
    this.router.navigate([`${this.config['MFS']['MODULE_URL']}/transects`, this.idSite, 'new_visit']);
  }

  onVisitDetails(id_base_visit: number) {
    this.router.navigate([`${this.config['MFS']['MODULE_URL']}/transects`, this.idSite, 'visit', id_base_visit]);
  }

  onRowSelect(event: any) {
    if (event.type === 'click') {
      this.onVisitDetails(event.row.id_base_visit);
    }
  }

  getPlots() {
    this.plotApi.getPlotByTransect(this.currentSite.properties?.id_transect).subscribe(
      data => {
        this.plotHierarchy = data as any[];
        this.plotDataSource.data = this.plotHierarchy;
      },
      error => {
        this.toastr.error('Erreur lors de la récupération des placettes', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  togglePlot(id_plot: number) {
    this.expandedPlots = { ...this.expandedPlots, [id_plot]: !this.expandedPlots[id_plot] };
  }

  onAddSensor(content) {
    this.sensorToEdit = null;
    this.formSensor = this.formBuilder.group({
      serial_number: [null, Validators.required],
      install_date: [null, Validators.required],
    });
    this.modalRef = this.modalService.open(content, { centered: true });
  }

  onSaveSensor() {
    let sensor = this.formSensor.value;

    if (this.isNew) {
      if (this.sensorToEdit !== null) {
        this.sensors[this.sensorToEditIndex] = sensor;
      } else {
        this.sensors.push(sensor);
      }
      this.modalRef.close();
    } else if (this.sensorToEdit) {
      sensor.id_sensor = this.sensorToEdit;
      sensor.id_transect = this.currentSite.properties?.id_transect;
      this.sensorApi.updateSensor(sensor).subscribe(
        data => {
          this.modalRef.close();
          this.getSensors();
          this.sensorToEdit = null;
          this.formTransect.markAsDirty();
          this.toastr.success('Capteur modifié avec succès', '', { positionClass: 'toast-top-right' });
        },
        error => {
          this.toastr.error('Erreur lors de la modification du capteur', '', { positionClass: 'toast-top-right' });
        }
      );
    } else {
      sensor.id_transect = this.currentSite.properties?.id_transect;
      this.sensorApi.addSensor(sensor).subscribe(
        data => {
          this.modalRef.close();
          this.getSensors();
          this.formTransect.markAsDirty();
          this.toastr.success('Capteur ajouté avec succès', '', { positionClass: 'toast-top-right' });
        },
        error => {
          this.toastr.error("Erreur lors de l'ajout du capteur", '', { positionClass: 'toast-top-right' });
        }
      );
    }
  }

  onDeleteSensor(id_sensor: any) {
    this.sensorApi.deleteSensor(id_sensor).subscribe(
      data => {
        this.getSensors();
        this.toastr.success('Capteur supprimé avec succès', '', { positionClass: 'toast-top-right' });
      },
      error => {
        this.toastr.error('Erreur lors de la suppression du capteur', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  onConfirmDelete(id_sensor: any, confirmContent: any, index?: number) {
    this.sensorToDelete = id_sensor;
    this.sensorToDeleteIndex = index;
    this.confirmModalRef = this.modalService.open(confirmContent, { centered: true });
  }

  onConfirmDeleteSensor() {
    if (this.isNew) {
      this.sensors.splice(this.sensorToDeleteIndex, 1);
      this.confirmModalRef.close();
      this.toastr.success('Capteur supprimé avec succès', '', { positionClass: 'toast-top-right' });
    } else {
      this.onDeleteSensor(this.sensorToDelete);
      this.confirmModalRef.close();
    }
  }

  onEditSensor(sensor: any, content: any, index?: number) {
    this.sensorToEdit = sensor.id_sensor;
    this.sensorToEditIndex = index;
    this.formSensor = this.formBuilder.group({
      serial_number: [sensor.serial_number, Validators.required],
      install_date: [sensor.install_date, Validators.required],
    });
    this.modalRef = this.modalService.open(content, { centered: true });
  }

  removePlot(plots: any[], target: any): boolean {
    const index = plots.indexOf(target);
    if (index !== -1) {
      plots.splice(index, 1);
      return true;
    }
    for (let plot of plots) {
      if (plot.sub_plots?.length > 0) {
        if (this.removePlot(plot.sub_plots, target)) return true;
      }
    }
    return false;
  }

  onConfirmDeletePlot(id_plot: number, confirmContent: any, index?: number, plot?: any) {
    this.plotToDelete = id_plot;
    this.plotToDeleteIndex = index;
    this.plotToDeleteObject = plot;
    this.confirmPlotModalRef = this.modalService.open(confirmContent, { centered: true });
  }

  onConfirmDeletePlotAction() {
    if (this.isNew) {
      this.removePlot(this.plotHierarchy, this.plotToDeleteObject);
      this.plotHierarchy = [...this.plotHierarchy];
      this.confirmPlotModalRef.close();
      this.toastr.success('Placette supprimée avec succès', '', { positionClass: 'toast-top-right' });
    } else {
      this.plotApi.deletePlot(this.plotToDelete).subscribe(
        data => {
          this.getPlots();
          this.confirmPlotModalRef.close();
          this.toastr.success('Placette supprimée avec succès', '', { positionClass: 'toast-top-right' });
        },
        error => {
          this.toastr.error('Erreur lors de la suppression de la placette', '', { positionClass: 'toast-top-right' });
        }
      );
    }
  }
  public taxonFormatter = (taxon: any) => {
    return taxon?.nom_complet ? taxon.nom_complet : '';
  };

  addNewTaxon(event: any) {
    this.formStation.patchValue({ cd_nom: event.item.cd_nom });
  }
  onEditPlot(plot: any, content: any, index?: number) {
    this.plotToEdit = plot;
    this.plotToEditIndex = index;
    this.formEditPlot = this.formBuilder.group({
      code_plot: [plot.code_plot, Validators.required],
      distance_plot: [plot.distance_plot],
    });
    this.modalRef = this.modalService.open(content, { centered: true });
  }

  onSaveEditPlot() {
    let formValue = this.formEditPlot.value;

    if (this.isNew) {
      Object.assign(this.plotToEdit, formValue);
      this.plotHierarchy = [...this.plotHierarchy];
      this.modalRef.close();
      this.toastr.success('Placette modifiée avec succès', '', { positionClass: 'toast-top-right' });
    } else {
      let plot = formValue;
      plot.id_plot = this.plotToEdit.id_plot;
      plot.id_transect = this.currentSite.properties?.id_transect;
      this.plotApi.updatePlot(plot).subscribe(
        data => {
          this.modalRef.close();
          this.getPlots();
          this.toastr.success('Placette modifiée avec succès', '', { positionClass: 'toast-top-right' });
        },
        error => {
          this.toastr.error('Erreur lors de la modification de la placette', '', { positionClass: 'toast-top-right' });
        }
      );
    }
  }

  getParentCode(id_parent: any): string {
    if (this.isNew) {
      const parent = this.findPlotById(this.plotHierarchy, id_parent);
      return parent ? parent.code_plot : '';
    }
    const flatPlots = this.getFlatPlots(this.plotHierarchy);
    const parent = flatPlots.find(p => p.id_plot === id_parent);
    return parent ? parent.code_plot : '';
  }

  onSelectStation(id_station: any) {
    if (!id_station || id_station === 'null') {
      this.selectedStation = null;
      this.formTransect.patchValue({ id_station: null });
      return;
    }
    this.stationApi.getOneStation(id_station).subscribe(
      (data: any) => {
        this.selectedStation = data;
        this.formTransect.patchValue({ id_station: id_station });
        this.stationApi.getTransectsByStation(id_station).subscribe((transects: any[]) => {
          this.selectedStationTransects = transects;
        });
      },
      error => {
        this.toastr.error('Erreur lors de la récupération de la station', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  onNewStation(content) {
    this.formStation = this.formBuilder.group({
      name: [null, Validators.required],
      remarks: [null],
      cd_nom: [null, Validators.required],
    });
    this.modalRef = this.modalService.open(content, { centered: true });
  }

  onSaveStation() {
    let station = this.formStation.value;
    this.stationApi.addStation(station).subscribe(
      (data: any) => {
        this.stations.push(data);
        this.stations = this.stations.sort((a, b) => a.properties.name.localeCompare(b.properties.name));
        this.selectedStation = data;
        this.formTransect.patchValue({ id_station: data.properties.id_station });
        this.modalRef.close();
        this.toastr.success('Station créée avec succès', '', { positionClass: 'toast-top-right' });
      },
      error => {
        this.toastr.error('Erreur lors de la création de la station', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  getFlatPlots(plots: any[], depth: number = 1): any[] {
    const maxDepth = this.storeService.sfsConfig.max_plot_depth;
    let result = [];
    plots.forEach(plot => {
      if (depth < maxDepth) {
        result.push({ ...plot, depth });
        if (plot.sub_plots?.length > 0) {
          result = result.concat(this.getFlatPlots(plot.sub_plots, depth + 1));
        }
      }
    });
    return result;
  }

  onEditCurrentStation(content: any) {
    this.stationToEdit = this.selectedStation;
    this.stationApi.getOneStation(this.selectedStation.properties.id_station).subscribe((data: any) => {
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
    });
  }
  addNewTaxonEdit(event: any) {
  this.formEditStation.patchValue({ cd_nom: event.item.cd_nom });
  }

    onSaveEditCurrentStation() {
    let station = this.formEditStation.value;
    station.id_station = this.stationToEdit.properties.id_station;
    this.stationApi.updateStation(station).subscribe(
      data => {
        this.modalRef.close();
        this.selectedStation = data;
        this.stationApi.getAllStations().subscribe((result: any) => {
          this.stations = result[1].features.sort((a, b) => a.properties.name.localeCompare(b.properties.name));
        });
        if (this.idSite) {
          this.transectApi.getOneTransect(this.idSite).subscribe(
            (site: any) => {
              this.currentSite = site;
              this.storeService.setCurrentSite(this.currentSite);
            }
          );
        }
        this.toastr.success('Station modifiée avec succès', '', { positionClass: 'toast-top-right' });
      },
      error => {
        this.toastr.error('Erreur lors de la modification de la station', '', { positionClass: 'toast-top-right' });
      }
    );
}


  onDeleteCurrentStation(content: any) {
    this.stationToDelete = this.selectedStation;
    this.confirmModalRef = this.modalService.open(content, { centered: true });
  }

  onConfirmDeleteCurrentStation() {
    this.stationApi.deleteStation(this.stationToDelete.properties.id_station).subscribe(
      data => {
        this.confirmModalRef.close();
        this.selectedStation = null;
        this.selectedStationTransects = [];
        this.formTransect.patchValue({ id_station: null });
        this.stationApi.getAllStations().subscribe((result: any) => {
          this.stations = result[1].features.sort((a, b) => a.properties.name.localeCompare(b.properties.name));
        });
        this.toastr.success('Station supprimée', '', { positionClass: 'toast-top-right' });
      },
      error => {
        this.toastr.error('Erreur lors de la suppression de la station', '', { positionClass: 'toast-top-right' });
      }
    );
  }

  ngOnDestroy() {
    this.storeService.queryString = this.storeService.queryString.delete('id_base_site');
  }
}