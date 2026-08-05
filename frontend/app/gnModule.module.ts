import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

// GeoNature
import { GN2CommonModule } from '@geonature_common/GN2Common.module';

// Services
import { StationService } from './station/station.service';
import { TransectService } from './transect/transect.service';
import { PlotService } from './plot/plot.service';
import { SensorService } from './sensor/sensor.service';
import { StoreService } from './shared/services/store.service';
import { UserService } from './core/services/user.service';
import { TaxonService } from './core/services/taxon.service';
import { VisitReportService } from './visit-report/visit-report.service';


// Components
import { StationListComponent } from './station/station-list/station-list.component';
import { TransectFormComponent } from './transect/transect-form/transect-form.component';
import { VisitReportFormComponent } from './visit-report/visit-report-form/visit-report-form.component';
import { PlotReleveComponent } from './plot/plot-releve/plot-releve.component';


// Routes
import { routes } from './gnModule.routes';

// Angular Material / CDK
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { MatTreeModule } from '@angular/material/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, MatPaginatorIntl } from '@angular/material/paginator';
import { FrenchPaginatorIntl } from './core/services/french-paginator-intl.service';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';


@NgModule({
  declarations: [StationListComponent, TransectFormComponent,VisitReportFormComponent,PlotReleveComponent],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTreeModule,
    MatIconModule,
    MatButtonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressBarModule,
    MatMenuModule,
    MatTooltipModule,
    NgxDatatableModule
  ],
  providers: [
    HttpClient,
    StationService,
    TransectService,
    PlotService,
    SensorService,
    VisitReportService,
    StoreService,
    UserService,
    TaxonService,
    { provide: MatPaginatorIntl, useClass: FrenchPaginatorIntl },
  ],
  bootstrap: [],
})
export class GeonatureModule {}