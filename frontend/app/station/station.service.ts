import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class StationService {
  constructor(
    private _http: HttpClient,
    private config: ConfigService,
  ) { }

  getAllStations(params?: any) {
    let myParams = new HttpParams();
    for (let key in params) {
      if (params[key]) myParams = myParams.set(key, params[key]);
    }
    return this._http.get(`${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations`, {
      params: myParams,
    });
  }

  getOneStation(id_station: any) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/${id_station}`
    );
  }

  addStation(station: any) {
    return this._http.post(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations`,
      station
    );
  }

  updateStation(station: any) {
    return this._http.patch(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/${station.id_station}`,
      station
    );
  }

  deleteStation(id_station: any) {
    return this._http.delete(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/${id_station}`
    );
  }

  getTransectsByStation(id_station: number) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/${id_station}/transects`
    );
  }

  getStationsYears() {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/years`
    );
  }

  getStationsArea() {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/area`
    );
  }

  getStationsTaxa() {
  return this._http.get(
    `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/taxa`
  );
  }

  getOrganism() {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/stations/organism`
    );
  }
  
}