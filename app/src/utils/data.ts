import type { Exam, ExamIndex } from '../types';

// 개발 환경에서는 로컬 data 폴더, 배포 시 GitHub raw URL 사용
const DATA_BASE_URL = import.meta.env.VITE_DATA_URL || `${import.meta.env.BASE_URL}data`;

export async function fetchExamIndex(): Promise<ExamIndex> {
  const res = await fetch(`${DATA_BASE_URL}/index.json`);
  if (!res.ok) throw new Error('Failed to fetch exam index');
  return res.json();
}

export async function fetchExam(examId: string): Promise<Exam> {
  const res = await fetch(`${DATA_BASE_URL}/questions/${examId}.json`);
  if (!res.ok) throw new Error(`Failed to fetch exam: ${examId}`);
  return res.json();
}

export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
