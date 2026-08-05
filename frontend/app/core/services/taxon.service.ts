import { Injectable } from '@angular/core';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class TaxonService {
  public readonly searchApiEndPoint: string;

  constructor(
    private config: ConfigService,
  ) {
    this.searchApiEndPoint = `${this.config.API_TAXHUB}/taxref/search/lb_nom`;
  }
}