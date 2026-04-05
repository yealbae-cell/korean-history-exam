export interface Choice {
  number: number;
  text: string;
}

export interface Question {
  id: number;
  question: string;
  description: string | null;
  image: string | null;
  choices: Choice[];
  answer: number;
  category: string;
  era: string;
}

export interface Exam {
  examId: string;
  year: number;
  round: number;
  date: string;
  totalQuestions: number;
  questions: Question[];
}

export interface ExamMeta {
  examId: string;
  year: number;
  round: number;
  date: string;
  totalQuestions: number;
  file: string;
}

export interface ExamIndex {
  exams: ExamMeta[];
  categories: string[];
  eras: string[];
}

export interface UserAnswer {
  questionId: number;
  examId: string;
  selected: number | null;
  correct: boolean;
  timestamp: number;
}

export interface WrongAnswer {
  examId: string;
  questionId: number;
  question: Question;
  wrongCount: number;
  lastAttempt: number;
}

export interface DailyStats {
  date: string;
  totalAnswered: number;
  correctCount: number;
}

export interface StudyRecord {
  wrongAnswers: Record<string, WrongAnswer>;
  dailyStats: DailyStats[];
  streak: number;
  lastStudyDate: string;
}
