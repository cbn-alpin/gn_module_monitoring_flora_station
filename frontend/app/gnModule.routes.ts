import { Routes } from '@angular/router';

import { StationListComponent } from './station/station-list/station-list.component';
import { TransectFormComponent } from './transect/transect-form/transect-form.component';
import { VisitReportFormComponent } from './visit-report/visit-report-form/visit-report-form.component';

export const routes: Routes = [
  { path: '', component: StationListComponent },
  { path: 'transects/new_transect', component: TransectFormComponent },
  { path: 'transects/:idSite', component: TransectFormComponent },
  { path: 'transects/:idSite/visit/:idVisit', component: VisitReportFormComponent },
  { path: 'transects/:idSite/new_visit', component: VisitReportFormComponent },
];