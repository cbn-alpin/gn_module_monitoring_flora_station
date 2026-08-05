import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class SensorService {
  constructor(
    private _http: HttpClient,
    private config: ConfigService,
  ) { }

  getSensorsByTransect(id_transect: any) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/transects/${id_transect}/sensors`
    );
  }

  addSensor(sensor: any) {
    return this._http.post(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/sensors`,
      sensor
    );
  }

  updateSensor(sensor: any) {
    return this._http.patch(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/sensors/${sensor.id_sensor}`,
      sensor
    );
  }

  deleteSensor(id_sensor: any) {
    return this._http.delete(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/sensors/${id_sensor}`
    );
  }
}