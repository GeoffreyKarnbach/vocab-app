import { Component, OnInit } from '@angular/core';
import { ExerciseService } from 'src/app/services';
import { SessionHistoryDto, PastSessionDto, WordDto } from 'src/app/dtos';

@Component({
  selector: 'app-example-page',
  templateUrl: './example-page.component.html',
  styleUrls: ['./example-page.component.scss'],
})
export class ExamplePageComponent implements OnInit {
  sessionHistory: SessionHistoryDto | null = null;
  currentPage: number = 1;
  pageSize: number = 5; // Number of sessions per page
  totalPages: number = 1;
  paginatedSessions: PastSessionDto[] = [];

  constructor(private exerciseService: ExerciseService) {}

  ngOnInit() {
    this.loadSessionHistory();
  }

  loadSessionHistory(): void {
    this.exerciseService.getPastSessions().subscribe(
      (response: SessionHistoryDto) => {
        this.sessionHistory = response;
        this.totalPages = Math.ceil(response.sessionCount / this.pageSize);
        this.updatePaginatedSessions();
      },
      (error) => {
        console.error('Error fetching session history:', error);
      }
    );
  }

  // Update the sessions to display based on the current page
  updatePaginatedSessions(): void {
    if (!this.sessionHistory) return;
    const startIndex = (this.currentPage - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.paginatedSessions = this.sessionHistory.history.slice(
      startIndex,
      endIndex
    );
    console.log('Paginated Sessions:', this.paginatedSessions);
  }

  // Pagination Methods
  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) {
      return;
    }
    this.currentPage = page;
    this.updatePaginatedSessions();
  }

  calculateAccuracy(word: WordDto): number {
    return (word.correctCount / word.totalCount) * 100;
  }

  calculateDifficulty(word: WordDto): number {
    return (word.totalCount - word.correctCount) / word.totalCount;
  }

  formatDuration(duration: number): string {
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
}
