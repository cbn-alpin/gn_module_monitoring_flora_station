import { Component, OnInit, AfterViewChecked,ViewChild } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { NgbDateParserFormatter } from '@ng-bootstrap/ng-bootstrap';
import { forkJoin } from 'rxjs/observable/forkJoin';
import { ToastrService } from 'ngx-toastr';
import * as _ from 'lodash';

import { CommonService } from '@geonature_common/service/common.service';
import { DataFormService } from '@geonature_common/form/data-form.service';
import { ConfigService } from '@geonature/services/config.service';

import { VisitReportService } from '../visit-report.service';
import { PlotService } from '../../plot/plot.service';
import { TransectService } from '../../transect/transect.service';
import { StoreService } from '../../shared/services/store.service';
import { UserService } from '../../core/services/user.service';
import { IVisit, PlotSurvey } from '../visit-report.model';
import { ISite } from '../../transect/transect.model';
import { PlotReleveComponent } from '../../plot/plot-releve/plot-releve.component';

@Component({
  selector: 'visit-report-form',
  templateUrl: 'visit-report-form.component.html',
  styleUrls: ['./visit-report-form.component.scss'],
})
export class VisitReportFormComponent implements OnInit, AfterViewChecked {
  idSite: number;
  idVisit: number;
  loadForm: boolean = false;
  visit: IVisit;
  isNew: boolean;
  public visit_name: string = 'Nouvelle visite';
  public id_base_site: number;
  public strata = [];
  public substrates = [];
  checked = 0;
  currentSite: ISite;
  plots: PlotSurvey[] = [];
  plotId: number;
  visitForm: FormGroup;
  plotTitle: string;
  submit_label: string;
  selectedPlot: PlotSurvey;
  spinner: boolean;
  public disabledForm: boolean = true;
  public edit_btn: string = 'Éditer';
  public updateIsAllowed: boolean = false;
  public addIsAllowed: boolean = false;
  public plotHierarchy = [];
  public expandedPlots: { [key: number]: boolean } = {};
  @ViewChild(PlotReleveComponent) plotReleveComponent!: PlotReleveComponent;
  public isSubPlot: boolean = false;

  constructor(
    private config: ConfigService,
    private activatedRoute: ActivatedRoute,
    private commonService: CommonService,
    public router: Router,
    private formBuilder: FormBuilder,
    public dateParser: NgbDateParserFormatter,
    public storeService: StoreService,
    private _api: VisitReportService,
    private plotApi: PlotService,
    private transectApi: TransectService,
    private toastr: ToastrService,
    private nomenclatureServ: DataFormService,
    private userService: UserService
  ) {}

 ngOnInit() {
    this.idSite = this.activatedRoute.snapshot.params['idSite'];
    this.idVisit = this.activatedRoute.snapshot.params['idVisit'];
    this.isNew = !this.idVisit;
    this.currentSite = this.storeService.getCurrentSite();
    this.initForm();

    if (!this.currentSite) {
      forkJoin([
        this.nomenclatureServ.getNomenclature('STRATE_PLACETTE', null, null, null, {
          orderby: 'label_default',
        }),
        this.nomenclatureServ.getNomenclature('SUBSTRAT_PLACETTE', null, null, null, {
          orderby: 'label_default',
        }),
        this.transectApi.getOneTransect(this.idSite),
      ]).subscribe(
        (results: any) => {
          this.strata = results[0] ? results[0].values : [];
          this.substrates = results[1] ? results[1].values : [];
          this.renameKey(this.strata, 'id_nomenclature_stratum');
          this.renameKey(this.substrates, 'id_nomenclature_substrate');
          this.currentSite = results[2];
          this.storeService.setCurrentSite(this.currentSite);
          this.id_base_site = this.currentSite.properties.id_base_site;
          this.plotId = this.currentSite.properties.cor_plots[0].id_plot;
          this.plotTitle = this.currentSite.properties.cor_plots[0].code_plot;
          this.getPlots();
          this.finishInit();
        },
        error => {
          this.toastr.error(
            'Une erreur est survenue lors de la récupération des informations sur le serveur.',
            '',
            { positionClass: 'toast-top-right' }
          );
        }
      );
    } else {
      this.plotId = this.currentSite.properties.cor_plots[0].id_plot;
      this.plotTitle = this.currentSite.properties.cor_plots[0].code_plot;
      this.id_base_site = this.currentSite.properties.id_base_site;
      this.getPlots();

      forkJoin([
        this.nomenclatureServ.getNomenclature('STRATE_PLACETTE', null, null, null, {
          orderby: 'label_default',
        }),
        this.nomenclatureServ.getNomenclature('SUBSTRAT_PLACETTE', null, null, null, {
          orderby: 'label_default',
        }),
      ]).subscribe(
        (results: any) => {
          this.strata = results[0] ? results[0].values : [];
          this.substrates = results[1] ? results[1].values : [];
          this.renameKey(this.strata, 'id_nomenclature_stratum');
          this.renameKey(this.substrates, 'id_nomenclature_substrate');
          this.finishInit();
        },
        error => {
          this.toastr.error(
            'Une erreur est survenue lors de la récupération des informations sur le serveur.',
            '',
            { positionClass: 'toast-top-right' }
          );
        }
      );
    }
}

  private finishInit() {
    if (!this.isNew) {
      this.getVisit();
      this.submit_label = 'Modifier la visite';
    } else {
      this.userService.check_user_cruved_visit('C', this.visit).subscribe(ucruved => {
        this.addIsAllowed = ucruved;
        this.loadForm = true;
      });
      this.disabledForm = false;
      this.visit = this._api.getDefaultVisit();
      this.submit_label = 'Enregistrer la visite';
    }
  }

  ngAfterViewChecked() {
    if (this.loadForm !== false && this.checked == 0) {
      this.checked++;
      this.patchForm();
    }
  }

  private renameKey(list, targetKey: string) {
    list.forEach(element => {
      element[targetKey] = element.id_nomenclature;
      delete element.id_nomenclature;
    });
  }

  private getVisit() {
    this._api.getOneVisit(this.idVisit).subscribe(
      (data: any) => {
        this.visit = data;
        this.userService.check_user_cruved_visit('U', this.visit).subscribe(ucruved => {
          this.updateIsAllowed = ucruved;
        });
        this.visit.perturbations = null;
        if (this.visit.cor_visit_perturbation) {
          this.visit.perturbations = this.visit.cor_visit_perturbation.map(
            (perturbation: any) => perturbation.t_nomenclature
          );
        }
        this.patchForm();
        this.plots = _.clone(this.visit.cor_releve_plot);
       
        this.selectedPlot = this.visit.cor_releve_plot.find(plot => {
          return plot.id_plot == this.plotId;
        });
        this.currentSite.properties.cor_plots.map((plotlist: any) => {
          if (
            !this.visit.cor_releve_plot.find(plot => {
              return plot.id_plot == plotlist.id_plot;
            })
          )
            plotlist.isEmpty = true;
        });
        this.visit_name = 'Visite N°' + this.visit.id_base_visit;
      },
      error => {
        if (error.status != 404) {
          this.toastr.error('Une erreur est survenue lors du chargement de votre relevé', '', {
            positionClass: 'toast-top-right',
          });
        }
      }
    );
  }

  getPlotSurvey(plotSurvey) {
    this.currentSite.properties.cor_plots.map((plot: any) => {
      if (plot.id_plot == plotSurvey[0].id_plot) {
        plot.status = plotSurvey[0].status;
        if (plotSurvey[1] == true) {
          plot.isModified = plotSurvey[1];
          plot.isEmpty = false;
        }
      }
    });

    let index = _.findIndex(this.plots, { id_plot: plotSurvey[0].id_plot });
    if (index >= 0) {
      this.plots.splice(index, 1, plotSurvey[0]);
    } else this.plots.push(plotSurvey[0]);

    if (
      _.find(this.plots, plot => {
        return plot.status == false;
      })
    )
      this.visitForm.controls['plots'].setErrors({ incorrect: true });
    else this.visitForm.controls['plots'].setErrors(null);
  }

  backToVisits() {
    this.router.navigate([`${this.config['MFS']['MODULE_URL']}/transects`, this.id_base_site]);
  }

  onChangePlot(plot) {
    if (this.plotReleveComponent) {
      this.plotReleveComponent.onFieldChange();
    }

    this.spinner = true;
    this.plotId = plot.id_plot;
    this.plotTitle = this.currentSite.properties.cor_plots.find(p => {
      return p.id_plot == this.plotId;
    }).code_plot;
    this.selectedPlot = this.plots.find(p => {
      return p.id_plot == this.plotId;
    });
    setTimeout(() => {
      this.spinner = false;
    }, 300);
}

  isActive(plot) {
    return this.plotId === plot.id_plot;
  }

  private initForm() {
    this.visitForm = this.formBuilder.group({
      id_base_visit: null,
      visit_date_min: [null, Validators.required],
      observers: [null, Validators.required],
      perturbations: new Array(),
      plots: null,
    });
    this.visitForm.controls['plots'].statusChanges.subscribe(status => {});
  }

onSubmitVisit() {
    if (this.plotReleveComponent) {
      this.plotReleveComponent.onFieldChange();
    }

    if (this.visitForm.valid) {
      let preparedData: any = {};
      preparedData['id_base_visit'] = this.visitForm.value['id_base_visit'];
      preparedData['observers'] = this.visitForm.value['observers'].map(obs => {
        return obs.id_role;
      });
      if (this.visitForm.value['perturbations'])
        preparedData['perturbations'] = this.visitForm.value['perturbations'].map(perturbation => {
          if (!perturbation.hasOwnProperty('id_nomenclature_disturbance')) {
            return { id_nomenclature_disturbance: perturbation.id_nomenclature };
          } else {
            return { id_nomenclature_disturbance: perturbation.id_nomenclature_disturbance };
          }
        });
      preparedData['visit_date_min'] = this.dateParser.format(
        this.visitForm.value['visit_date_min']
      );
      preparedData['id_base_site'] = this.id_base_site;

      const plotsPayload = this.plots.map((plot: any) => {
        const preparedPlot = _.cloneDeep(plot);
        delete preparedPlot.status;
        delete preparedPlot.isEmpty;
        delete preparedPlot.isModified;

        if (preparedPlot.strata_survey) {
          preparedPlot.strata_survey = preparedPlot.strata_survey.map(stratum => {
            const { label_default, ...rest } = stratum;
            return rest;
          });
        }
        if (preparedPlot.substrates_survey) {
          preparedPlot.substrates_survey = preparedPlot.substrates_survey.map(substrate => {
            const { label_default, ...rest } = substrate;
            return rest;
          });
        }
        if (preparedPlot.disturbances_survey) {
          preparedPlot.disturbances_survey = preparedPlot.disturbances_survey.map(disturbance => ({
            id_nomenclature_disturbance:
              disturbance.id_nomenclature_disturbance ?? disturbance.id_nomenclature,
          }));
        }
        return preparedPlot;
      });

      preparedData['plots'] = plotsPayload;
      this.sendFormData(preparedData);
    }
}
  private sendFormData(preparedData) {
    if (this.isNew) {
      this._api.addVisit(preparedData).subscribe(
        result => this.onDataSavedSuccess(result),
        error => this.onDataSavedError(error)
      );
    } else {
      this._api.updateVisit({ idVisit: this.idVisit, data: preparedData }).subscribe(
        result => this.onDataSavedSuccess(result),
        error => this.onDataSavedError(error)
      );
    }
  }

  private onDataSavedSuccess(result) {
    this.toastr.success('Visite enregistrée avec succès', '', {
      positionClass: 'toast-top-right',
    });
    this.backToVisits();
  }

  private onDataSavedError(error) {
    if (error.status === 409 && error.error?.description?.startsWith('PostYearError')) {
      this.visitForm.controls['visit_date_min'].setErrors({ dateExist: true });
      const title = 'Une visite existe déjà sur ce site pour cette année !';
      const msg = this.isNew
        ? "Veuillez plutôt éditer l'ancienne visite."
        : "Veuillez corriger l'année de la date de cette visite.";
      const options = {
        positionClass: 'toast-top-center',
        timeOut: 5000,
      };
      this.toastr.warning(msg, title, options);
    } else {
      this.commonService.translateToaster('error', 'ErrorMessage');
    }
    console.log(error);
  }

  onEdit() {
    this.disabledForm = !this.disabledForm;
    if (!this.disabledForm) {
      this.edit_btn = 'Annuler';
    } else {
      this.visitForm.reset();
      this.plots = _.clone(this.visit.cor_releve_plot);
      this.currentSite.properties.cor_plots.map((plotlist: any) => {
        plotlist.isModified = false;
        if (
          !this.visit.cor_releve_plot.find(plot => {
            return plot.id_plot == plotlist.id_plot;
          })
        )
          plotlist.isEmpty = true;
      });
      this.patchForm();
      this.edit_btn = 'Éditer';
    }
  }

  private patchForm() {
    this.visitForm.patchValue({
      id_base_visit: this.idVisit,
      visit_date_min: this.dateParser.parse(this.visit.visit_date_min),
      observers: this.visit.observers,
      perturbations: this.visit.perturbations,
    });
    this.loadForm = true;
  }

  resizeCard() {
    return this.updateIsAllowed || this.addIsAllowed;
  }

  getPlots() {
    this.plotApi.getPlotByTransect(this.currentSite.properties?.id_transect).subscribe(
      (data: any[]) => {
        this.plotHierarchy = data;
      },
      error => {
        this.toastr.error('Erreur lors de la récupération des placettes', '', {
          positionClass: 'toast-top-right',
        });
      }
    );
  }

  togglePlot(id_plot: number) {
    this.expandedPlots = {
      ...this.expandedPlots,
      [id_plot]: !this.expandedPlots[id_plot],
    };
  }
}