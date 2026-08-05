import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class PlotService {
  constructor(
    private _http: HttpClient,
    private config: ConfigService,
  ) { }

  getPlotByTransect(id_transect: any) {
    return this._http.get(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/transects/${id_transect}/plots`
    );
  }

  addPlot(plot: any) {
    return this._http.post(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/plots`,
      plot
    );
  }

  updatePlot(plot: any) {
    return this._http.patch(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/plots/${plot.id_plot}`,
      plot
    );
  }

  deletePlot(id_plot: any) {
    return this._http.delete(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/plots/${id_plot}`
    );
  }
}