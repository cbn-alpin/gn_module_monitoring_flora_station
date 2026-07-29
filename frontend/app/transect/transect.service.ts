import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class TransectService {
  constructor(
    private _http: HttpClient,
    private config: ConfigService,
  ) { }

  getAllTransects(params: any) {
    let myParams = new HttpParams();
    for (let key in params) {
      if (params[key]) myParams = myParams.set(key, params[key]);
    }
    return this._http.get(`${this.config.API_ENDPOINT}${this.config['SFS']['MODULE_URL']}/transects`, {
      params: myParams,
    });
  }

  getOneTransect(idSite: any) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['SFS']['MODULE_URL']}/transects/${idSite}`
    );
  }

  addTransect(transect: any) {
    return this._http.post(
      `${this.config.API_ENDPOINT}${this.config['SFS']['MODULE_URL']}/transects`,
      transect
    );
  }

  updateTransect(transect: any) {
    return this._http.patch(
      `${this.config.API_ENDPOINT}${this.config['SFS']['MODULE_URL']}/transects/${transect.id_transect}`,
      transect
    );
  }

  getAllSites(params: any) {
    let myParams = new HttpParams();
    for (let key in params) {
      if (params[key]) myParams = myParams.set(key, params[key]);
    }
    return this._http.get(`${this.config.API_ENDPOINT}${this.config['SFS']['MODULE_URL']}/sites`, {
      params: myParams,
    });
  }
}