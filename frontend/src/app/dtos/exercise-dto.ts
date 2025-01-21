export interface ExerciseItemDto {
  id: number;
  english: string;
  romanian: string;
}

export interface CompletedExerciseDto {
  wordResults: Array<{ wordId: number; correct: boolean }>;
  timestamp: string;
  duration: number;
}

export interface PastSessionDto {
  timestamp: string;
  correct_words: number;
  total_words: number;
  duration: number;
}

export interface SessionHistoryDto {
  history: PastSessionDto[];
  sessionCount: number;
  totalCorrect: number;
  totalWords: number;
  totalDuration: number;
  mostPracticedWords: WordDto[];
  mostAccurateWords: WordDto[];
  mostDifficultWords: WordDto[];
}

export interface WordDto {
  id: number;
  english: string;
  romanian: string;
  correctCount: number;
  totalCount: number;
}
