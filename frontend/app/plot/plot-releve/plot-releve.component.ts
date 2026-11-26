import { Component, Output, Input, EventEmitter, OnChanges, OnDestroy } from '@angular/core';
import { FormGroup, FormBuilder, FormArray, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import * as _ from 'lodash';

@Component({
  selector: 'plot-releve',
  templateUrl: 'plot-releve.component.html',
  styleUrls: ['./plot-releve.component.scss'],
})
export class PlotReleveComponent implements OnChanges, OnDestroy {
  @Input() strata?: any[];
  @Input() substrates?: any[];
  @Input('plot-id') plotId?: number;
  @Input() data: any = null;
  @Input() disabledForm: any;
  @Input() title?: string;
  @Input() isSubPlot: boolean = false;
  @Output() plotSurvey = new EventEmitter();
  private isModified: boolean = false;
  private plotSurveyId?: number;
  plotForm?: FormGroup;
  hasStrataCovering?: boolean;
  hasSubstrateCovering?: boolean;
  private valueChangesSubscription?: Subscription;

  constructor(
    private formBuilder: FormBuilder,
  ) { }

  ngOnChanges() {
    this.hasStrataCovering = false;
    this.hasSubstrateCovering = false;

    this.initPlotForm();
    this.initStrata();
    this.initSubstrates();

    this.plotForm?.enable();
    if (this.disabledForm) {
      this.plotForm?.disable();
    }

    this.plotSurveyId = undefined;
    if (this.data) {
      this.plotSurveyId = this.data.id_plot_survey;
      this.patchForm();
    }

    this.onChanges();
  }

  private initPlotForm() {
    this.plotForm = this.formBuilder.group({
      is_exclosure: false,
      taxon_present: false,
      remarks: null,
      flowering_stems_count: [null, Validators.min(0)],
      non_flowering_stems_count: [null, Validators.min(0)],
      strata_survey: this.formBuilder.array([]),
      substrates_survey: this.formBuilder.array([]),
      disturbances_survey: [[]],
    });
  }

  private initStrata(): void {
    this.strata
      ?.sort((a, b) => a.hierarchy.localeCompare(b.hierarchy))
      .forEach(stratum => {
        (this.plotForm?.get('strata_survey') as FormArray).push(
          this.formBuilder.group({
            id_nomenclature_stratum: [stratum.id_nomenclature_stratum],
            id_plot_survey_stratum: [null],
            cover_percentage: [null, Validators.compose([Validators.min(0), Validators.max(100)])],
            label_default: [stratum.label_default],
            definition_default: [stratum.definition_default],
          })
        );
      });
  }

  private initSubstrates(): void {
    this.substrates
      ?.sort((a, b) => a.hierarchy.localeCompare(b.hierarchy))
      .forEach(substrate => {
        (this.plotForm?.get('substrates_survey') as FormArray).push(
          this.formBuilder.group({
            id_nomenclature_substrate: [substrate.id_nomenclature_substrate],
            id_plot_survey_substrate: [null],
            cover_percentage: [null, Validators.compose([Validators.min(0), Validators.max(100)])],
            label_default: [substrate.label_default],
            definition_default: [substrate.definition_default],
          })
        );
      });
  }

 private patchForm() {
    const disturbances = (this.data.disturbances_survey || [])
      .map((d: { t_nomenclature: any }) => d.t_nomenclature || d)
      .filter(Boolean);

    this.plotForm?.patchValue({
      is_exclosure: this.data.is_exclosure,
      taxon_present: this.data.taxon_present,
      remarks: this.data.remarks,
      flowering_stems_count: this.data.flowering_stems_count,
      non_flowering_stems_count: this.data.non_flowering_stems_count,
      disturbances_survey: disturbances,
    });
    
    for (const item of this.data.strata_survey || []) {
      if (item.cover_percentage != null) {
        this.hasStrataCovering = true;
      }
      for (const control of (this.plotForm?.get('strata_survey') as FormArray)?.controls) {
        if (item.id_nomenclature_stratum == control.value.id_nomenclature_stratum) {
          control.patchValue({
            cover_percentage: item.cover_percentage,
            id_plot_survey_stratum: item.id_plot_survey_stratum,
          });
          break;
        }
      }
    }

    for (const item of this.data.substrates_survey || []) {
      if (item.cover_percentage != null) {
        this.hasSubstrateCovering = true;
      }
      for (const control of (this.plotForm?.get('substrates_survey') as FormArray).controls) {
        if (item.id_nomenclature_substrate == control.value.id_nomenclature_substrate) {
          control.patchValue({
            cover_percentage: item.cover_percentage,
            id_plot_survey_substrate: item.id_plot_survey_substrate,
          });
          break;
        }
      }
    }
}

  private onChanges(): void {
    if (this.valueChangesSubscription) {
      this.valueChangesSubscription.unsubscribe();
    }
    this.valueChangesSubscription = this.plotForm?.valueChanges.subscribe(val => {
      this.isModified = true;
    });
}



  onFieldChange() {
    const formValue = _.cloneDeep(this.plotForm?.value);

    formValue.strata_survey = formValue.strata_survey.map((stratum: {label_default:any,definition_default:any}) => {
      delete stratum.label_default;
      delete stratum.definition_default;
      return stratum;
    });

    formValue.substrates_survey = formValue.substrates_survey.map((substrate: {label_default:any,definition_default:any}) => {
      delete substrate.label_default;
      delete substrate.definition_default;
      return substrate;
    });

    const payload: any = {
      id_plot: this.plotId,
      ...formValue,
      status: this.plotForm?.valid,
    };
    if (this.plotSurveyId) {
      payload.id_plot_survey = this.plotSurveyId;
    }

    this.plotSurvey.emit([payload, this.isModified]);
    this.isModified = false;
}
ngOnDestroy() {
    if (this.valueChangesSubscription) {
      this.valueChangesSubscription.unsubscribe();
    }
}

}