import { Routes } from '@angular/router';

import { StationListComponent } from './station/station-list/station-list.component';
import { TransectFormComponent } from './transect/transect-form/transect-form.component';

export const routes: Routes = [
  { path: '', component: StationListComponent },
  { path: 'transects/new_transect', component: TransectFormComponent },
  { path: 'transects/:idSite', component: TransectFormComponent },
];