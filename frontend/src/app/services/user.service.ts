import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Globals } from 'src/app/global';
import { map, Observable, tap } from 'rxjs';
import { LoginRegisterDto } from '../dtos';
import { ToastService } from './toast.service';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private userBaseUri: string = this.globals.backendUri + '/user';

  constructor(
    private toastService: ToastService,
    private httpClient: HttpClient,
    private globals: Globals
  ) {}

  register(loginRegisterDto: LoginRegisterDto): Observable<string> {
    return this.httpClient
      .post<string>(this.userBaseUri + '/register', loginRegisterDto, {
        responseType: 'text' as 'json',
      })
      .pipe(
        tap((authResponse: string) => this.saveCurrentUserToken(authResponse))
      );
  }

  login(loginRegisterDto: LoginRegisterDto): Observable<string> {
    return this.httpClient
      .post<string>(this.userBaseUri + '/login', loginRegisterDto, {
        responseType: 'text' as 'json',
      })
      .pipe(
        tap((authResponse: string) => this.saveCurrentUserToken(authResponse))
      );
  }

  deleteAccount(): Observable<void> {
    return this.httpClient.delete<void>(this.userBaseUri + '/delete').pipe(
      tap(() => {
        localStorage.removeItem('token');
      })
    );
  }

  saveCurrentUserToken(token: string): void {
    // token is actually a map, we want the value of the "token" key
    console.log(token);
    const tokenValue = JSON.parse(token).token;
    localStorage.setItem('jwt', tokenValue);
  }

  logout(): void {
    localStorage.removeItem('jwt');
    this.toastService.showSuccess('Successfully logged out', 'Success');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('jwt');
  }

  getToken(): string {
    let token = localStorage.getItem('jwt');
    if (!token) {
      return '';
    }
    return token;
  }
}
