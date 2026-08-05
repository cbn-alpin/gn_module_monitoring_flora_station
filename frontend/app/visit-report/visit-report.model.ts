export interface PlotSurveyData {
  is_exclosure?: boolean;
  remarks?: string;
  taxon_present?: boolean;
  flowering_stems_count?: number;
  non_flowering_stems_count?: number;
  strata_survey?: any[];
  substrates_survey?: any[];
  disturbances_survey?: any[];
}

export interface PlotSurvey {
  id_plot_survey?: number;
  id_plot: number;
  plot_data: PlotSurveyData;
  status?: boolean;
  isEmpty?: boolean;
  isModified?: boolean;
}

export interface IVisit {
  id_base_visit?: number;
  id_base_site?: number;
  visit_date_min?: string;
  observers?: any[];
  perturbations?: any[];
  cor_visit_perturbation?: any[];
  cor_releve_plot?: PlotSurvey[];
}