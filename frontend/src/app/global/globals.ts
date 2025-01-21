import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class Globals {
  readonly backendUri: string = this.findBackendUrl();

  private findBackendUrl(): string {
    if (window.location.port === '4200') {
      // local `ng serve`, backend at localhost:8080
      return 'http://127.0.0.1:8888';
    } else {
      // assume deployed somewhere and backend is available at same host/port as frontend
      return (
        window.location.protocol +
        '//' +
        window.location.host +
        window.location.pathname +
        'api/v1'
      );
    }
  }
}
