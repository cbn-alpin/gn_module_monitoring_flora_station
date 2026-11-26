import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

@Injectable()
export class UserService {

   get currentUser() {
    return this.getUser();
  }


  private _cruved = {};

  constructor(
    private _http: HttpClient,
    private config: ConfigService,
  ) {
    
  }
   
  getUser() {
    const currentUser = localStorage.getItem('gn_current_user');
    if (currentUser) return JSON.parse(currentUser);
  }

  getCurrentUserRights() {
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}${this.config['MFS']['MODULE_URL']}/users/current/cruved`
    );
  }

  // Use service geonature ? localstorage ?
  getUserCruved() {
    if (Object.keys(this._cruved).length == 0) {
      return this.getCurrentUserRights();
    } else {
      return new Observable(ucruved => ucruved.next(this._cruved));
    }
  }


  check_user_cruved_visit(action: any, visit?: any):Observable<any> {
    let isAllowed = false;
    return new Observable(observer => {
      this.getUserCruved().subscribe(
        ucruved => {
          this._cruved = ucruved;
          let user_cruved_level = ucruved[action];
          if (visit) {
            if (user_cruved_level == '1') {
              visit.observers.forEach(observer => {
                if (observer.id_role == this.currentUser.id_role) {
                  isAllowed = true;
                } else if (visit.id_digitiser == this.currentUser.id_role) {
                  isAllowed = true;
                }
              });
            }

            if (user_cruved_level == '2') {
              visit.observers.forEach(observer => {
                if (observer.id_role == this.currentUser.id_role) {
                  isAllowed = true;
                } else if (visit.id_digitiser == this.currentUser.id_role) {
                  isAllowed = true;
                } else if (visit.id_organisme == this.currentUser.id_organisme) {
                  isAllowed = true;
                }
              });
            }
          }

          if (user_cruved_level == '3') {
            isAllowed = true;
          }

          observer.next(isAllowed);
        },
        error => {
          observer.error(error);
          console.error('Error userCruved: ', error);
        }
      );
    });
  }

  check_isAdmin(action: any): Observable<any> {
    let isAllowed = false;
    return new Observable(observer => {
      this.getUserCruved().subscribe(
        ucruved => {
          this._cruved = ucruved;
          let user_cruved_level = ucruved[action];
          if (user_cruved_level == '3') isAllowed = true;
          observer.next(isAllowed);
        },
        error => {
          observer.error(error);
          console.error('Error userCruved: ', error);
        }
      );
    });
  }

  check_user_cruved(action: any): Observable<any> {
    let isAllowed = false;
    return new Observable(observer => {
      this.getUserCruved().subscribe(
        ucruved => {
          this._cruved = ucruved;
          let user_cruved_level = parseInt(ucruved[action]);
          if (user_cruved_level > 0) {
            isAllowed = true;
          }
          observer.next(isAllowed);
        },
        error => {
          observer.error(error);
          console.error('Error userCruved: ', error);
        }
      );
    });
  }
}