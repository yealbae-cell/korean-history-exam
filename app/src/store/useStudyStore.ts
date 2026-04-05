import { useState, useEffect, useCallback } from 'react';
import type { Question, WrongAnswer, DailyStats, StudyRecord } from '../types';

const STORAGE_KEY = 'korean-history-study';

function getInitialRecord(): StudyRecord {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {
    // ignore
  }
  return {
    wrongAnswers: {},
    dailyStats: [],
    streak: 0,
    lastStudyDate: '',
  };
}

function saveRecord(record: StudyRecord) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
}

function getTodayStr(): string {
  return new Date().toISOString().split('T')[0];
}

export function useStudyStore() {
  const [record, setRecord] = useState<StudyRecord>(getInitialRecord);

  useEffect(() => {
    saveRecord(record);
  }, [record]);

  const recordAnswer = useCallback(
    (examId: string, question: Question, selected: number) => {
      setRecord((prev) => {
        const next = { ...prev };
        const isCorrect = selected === question.answer;
        const today = getTodayStr();
        const key = `${examId}-${question.id}`;

        // 오답 기록
        if (!isCorrect) {
          const existing = next.wrongAnswers[key];
          next.wrongAnswers = {
            ...next.wrongAnswers,
            [key]: {
              examId,
              questionId: question.id,
              question,
              wrongCount: (existing?.wrongCount ?? 0) + 1,
              lastAttempt: Date.now(),
            },
          };
        } else {
          // 정답이면 오답노트에서 제거
          const { [key]: _, ...rest } = next.wrongAnswers;
          next.wrongAnswers = rest;
        }

        // 일별 통계
        const stats = [...next.dailyStats];
        const todayIdx = stats.findIndex((s) => s.date === today);
        if (todayIdx >= 0) {
          stats[todayIdx] = {
            ...stats[todayIdx],
            totalAnswered: stats[todayIdx].totalAnswered + 1,
            correctCount: stats[todayIdx].correctCount + (isCorrect ? 1 : 0),
          };
        } else {
          stats.push({
            date: today,
            totalAnswered: 1,
            correctCount: isCorrect ? 1 : 0,
          });
        }
        next.dailyStats = stats;

        // 스트릭 계산
        if (next.lastStudyDate !== today) {
          const yesterday = new Date();
          yesterday.setDate(yesterday.getDate() - 1);
          const yesterdayStr = yesterday.toISOString().split('T')[0];
          next.streak =
            next.lastStudyDate === yesterdayStr ? next.streak + 1 : 1;
          next.lastStudyDate = today;
        }

        return next;
      });
    },
    []
  );

  const getWrongAnswers = useCallback((): WrongAnswer[] => {
    return Object.values(record.wrongAnswers).sort(
      (a, b) => b.lastAttempt - a.lastAttempt
    );
  }, [record.wrongAnswers]);

  const getDailyStats = useCallback((): DailyStats[] => {
    return [...record.dailyStats].sort((a, b) => a.date.localeCompare(b.date));
  }, [record.dailyStats]);

  const getTotalStats = useCallback(() => {
    const stats = record.dailyStats;
    const totalAnswered = stats.reduce((s, d) => s + d.totalAnswered, 0);
    const totalCorrect = stats.reduce((s, d) => s + d.correctCount, 0);
    return {
      totalAnswered,
      totalCorrect,
      accuracy: totalAnswered > 0 ? (totalCorrect / totalAnswered) * 100 : 0,
      streak: record.streak,
      totalDays: stats.length,
    };
  }, [record.dailyStats, record.streak]);

  const clearData = useCallback(() => {
    const fresh: StudyRecord = {
      wrongAnswers: {},
      dailyStats: [],
      streak: 0,
      lastStudyDate: '',
    };
    setRecord(fresh);
  }, []);

  return {
    recordAnswer,
    getWrongAnswers,
    getDailyStats,
    getTotalStats,
    clearData,
  };
}
