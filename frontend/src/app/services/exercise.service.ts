import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Globals } from 'src/app/global';
import { map, Observable, tap } from 'rxjs';
import {
  CompletedExerciseDto,
  ExerciseItemDto,
  LoginRegisterDto,
  PastSessionDto,
  SessionHistoryDto,
} from '../dtos';
import { ToastService } from './toast.service';

@Injectable({
  providedIn: 'root',
})
export class ExerciseService {
  private baseUri: string = this.globals.backendUri;

  constructor(
    private toastService: ToastService,
    private httpClient: HttpClient,
    private globals: Globals
  ) {}

  getExercise(): Observable<ExerciseItemDto[]> {
    return this.httpClient.get<ExerciseItemDto[]>(this.baseUri + '/exercise');
  }

  saveSession(session: CompletedExerciseDto): Observable<boolean> {
    return this.httpClient.post<boolean>(this.baseUri + '/session', session);
  }

  getPastSessions(): Observable<SessionHistoryDto> {
    return this.httpClient.get<SessionHistoryDto>(this.baseUri + '/history');
  }
}
