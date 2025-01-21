import { Component } from '@angular/core';
import { ExerciseService, ToastService } from 'src/app/services';
import { ExerciseItemDto, CompletedExerciseDto } from 'src/app/dtos';
import { Router } from '@angular/router';

@Component({
  selector: 'app-exercise',
  templateUrl: './exercise.component.html',
  styleUrls: ['./exercise.component.scss'],
})
export class ExerciseComponent {
  exerciseItems: ExerciseItemDto[] = [];
  currentItemIndex: number = 0;
  selectedAnswer: string | null = null;
  correctCount: number = 0;
  totalCount: number = 0;
  completedExercise: CompletedExerciseDto = {
    wordResults: [],
    timestamp: '',
    duration: 0,
  };
  startTime: number = 0;
  options: string[] = [];

  showTranslations: boolean = false;
  answerMarked: boolean = false;

  constructor(
    private exerciseService: ExerciseService,
    private toastService: ToastService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadExercise();
  }

  loadExercise() {
    this.exerciseService.getExercise().subscribe(
      (response) => {
        this.exerciseItems = response;
        this.loadOptions();
        this.startTimer();
      },
      (error) => {
        console.error(error);
      }
    );
  }

  loadOptions() {
    if (
      this.exerciseItems.length > 0 &&
      this.currentItemIndex < this.exerciseItems.length
    ) {
      const correctWord = this.exerciseItems[this.currentItemIndex];
      this.options = this.generateOptions(correctWord.english);
    }
  }

  generateOptions(correctTranslation: string): string[] {
    let options = new Set<string>([correctTranslation]);

    // Add 4 random words to the options (not the correct one)
    while (options.size < 5) {
      const randomWord =
        this.exerciseItems[
          Math.floor(Math.random() * this.exerciseItems.length)
        ].english;
      options.add(randomWord);
    }

    // Mix the options, randomize the order
    options = new Set([...options].sort(() => Math.random() - 0.5));

    return [...options];
  }

  startTimer() {
    this.startTime = Date.now();
  }

  markAnswer(selectedTranslation: string) {
    if (this.answerMarked) {
      return;
    }

    const correctWord = this.exerciseItems[this.currentItemIndex];
    const isCorrect = selectedTranslation === correctWord.english;

    if (isCorrect) {
      this.correctCount++;
    }

    this.completedExercise.wordResults.push({
      wordId: correctWord.id,
      correct: isCorrect,
    });

    this.totalCount++;
    this.selectedAnswer = selectedTranslation;

    this.showTranslations = true;
    this.answerMarked = true;
  }

  showNextWord() {
    if (this.currentItemIndex + 1 < this.exerciseItems.length) {
      this.currentItemIndex++;
      this.selectedAnswer = null;
      this.showTranslations = false;
      this.answerMarked = false;
      this.loadOptions();
    } else {
      this.submitExercise();
    }
  }

  submitExercise() {
    const duration = (Date.now() - this.startTime) / 1000; // in seconds
    this.completedExercise.timestamp = new Date().toISOString();
    this.completedExercise.duration = duration;

    this.exerciseService.saveSession(this.completedExercise).subscribe(
      (response) => {
        this.toastService.showSuccess('Exercise completed! 🎉', 'Success');
        this.router.navigate(['/']);
      },
      (error) => {
        console.error('Error submitting exercise:', error);
      }
    );
  }
}
