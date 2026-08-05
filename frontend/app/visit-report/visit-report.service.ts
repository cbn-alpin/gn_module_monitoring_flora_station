import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class VisitReportService {
  constructor(
    private _http: HttpClient,
    private config: ConfigService,
  ) {}

  getAllVisits(id_site: any) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/sites/${id_site}/visits`
    );
  }

  getOneVisit(id_visit: any) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/visits/${id_visit}`
    );
  }

  addVisit(visit: any) {
    return this._http.post(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/visits`,
      visit
    );
  }

  updateVisit(payload: { idVisit: any; data: any }) {
    return this._http.patch(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/visits/${payload.idVisit}`,
      payload.data
    );
  }

  getDefaultVisit() {
    return { id_base_visit: null, observers: [], perturbations: [], cor_releve_plot: [] };
  }
}