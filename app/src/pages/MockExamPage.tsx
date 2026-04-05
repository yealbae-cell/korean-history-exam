import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import type { Question } from '../types';
import { fetchExamIndex, fetchExam, shuffleArray } from '../utils/data';
import { useStudyStore } from '../store/useStudyStore';
import QuestionCard from '../components/QuestionCard';
import Timer from '../components/Timer';

const MOCK_EXAM_SIZE = 50;
const MOCK_EXAM_MINUTES = 80;

export default function MockExamPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<(Question & { examId: string })[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitted, setSubmitted] = useState(false);
  const [timerRunning, setTimerRunning] = useState(true);
  const { recordAnswer } = useStudyStore();

  useEffect(() => {
    loadRandomQuestions();
  }, []);

  async function loadRandomQuestions() {
    try {
      const index = await fetchExamIndex();
      const allQuestions: (Question & { examId: string })[] = [];

      for (const meta of index.exams) {
        const exam = await fetchExam(meta.examId);
        for (const q of exam.questions) {
          allQuestions.push({ ...q, examId: exam.examId });
        }
      }

      const shuffled = shuffleArray(allQuestions).slice(0, MOCK_EXAM_SIZE);
      setQuestions(shuffled);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleTimeUp = useCallback(() => {
    setTimerRunning(false);
    setSubmitted(true);
  }, []);

  if (loading) return <Container><Center>문제를 섞는 중...</Center></Container>;
  if (questions.length === 0) return <Container><Center>문제 데이터가 없습니다.</Center></Container>;

  const current = questions[currentIdx];
  const key = `${current.examId}-${current.id}`;

  const handleSelect = (choiceNum: number) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [key]: choiceNum }));
    recordAnswer(current.examId, current, choiceNum);
  };

  const handleSubmit = () => {
    setTimerRunning(false);
    setSubmitted(true);
  };

  const correctCount = questions.filter(
    (q) => answers[`${q.examId}-${q.id}`] === q.answer
  ).length;

  if (submitted) {
    return (
      <Container>
        <ResultSection>
          <ResultTitle>모의고사 결과</ResultTitle>
          <ScoreBox>
            <ScoreNum>{correctCount}</ScoreNum>
            <ScoreDivider>/</ScoreDivider>
            <ScoreTotal>{questions.length}</ScoreTotal>
          </ScoreBox>
          <ScorePercent>
            정답률 {((correctCount / questions.length) * 100).toFixed(1)}%
          </ScorePercent>
          <GradeInfo>
            {correctCount >= 40 ? '1급 합격!' : correctCount >= 35 ? '2급 합격!' : correctCount >= 30 ? '3급 합격!' : '불합격'}
          </GradeInfo>
          <ResultButtons>
            <ResultButton onClick={() => navigate('/')}>홈으로</ResultButton>
            <ResultButton onClick={() => navigate('/wrong-answers')}>
              오답노트
            </ResultButton>
            <ResultButton onClick={() => window.location.reload()}>
              다시 풀기
            </ResultButton>
          </ResultButtons>
        </ResultSection>
      </Container>
    );
  }

  return (
    <Container>
      <MockHeader>
        <BackButton onClick={() => navigate('/')}>← 중단</BackButton>
        <Timer
          initialMinutes={MOCK_EXAM_MINUTES}
          onTimeUp={handleTimeUp}
          running={timerRunning}
        />
        <Progress>
          {Object.keys(answers).length}/{questions.length}
        </Progress>
      </MockHeader>

      <QuestionCard
        question={current}

        total={questions.length}
        selectedAnswer={answers[key] ?? null}
        showResult={false}
        onSelect={handleSelect}
      />

      <NavButtons>
        <NavButton
          onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
          disabled={currentIdx === 0}
        >
          ← 이전
        </NavButton>
        <QuestionNav>{currentIdx + 1} / {questions.length}</QuestionNav>
        {currentIdx === questions.length - 1 ? (
          <SubmitButton onClick={handleSubmit}>제출하기</SubmitButton>
        ) : (
          <NavButton
            onClick={() => setCurrentIdx((i) => Math.min(questions.length - 1, i + 1))}
          >
            다음 →
          </NavButton>
        )}
      </NavButtons>

      <QuestionGrid>
        {questions.map((q, i) => {
          const qKey = `${q.examId}-${q.id}`;
          return (
            <GridItem
              key={qKey}
              $answered={qKey in answers}
              $current={i === currentIdx}
              onClick={() => setCurrentIdx(i)}
            >
              {i + 1}
            </GridItem>
          );
        })}
      </QuestionGrid>
    </Container>
  );
}

const Container = styled.div`
  max-width: 700px;
  margin: 0 auto;
  padding: 24px;
`;

const Center = styled.div`
  text-align: center;
  padding: 60px 0;
  color: #888;
`;

const MockHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
`;

const BackButton = styled.button`
  background: none;
  border: 1px solid #dee2e6;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
`;

const Progress = styled.span`
  font-size: 14px;
  color: #868e96;
  font-weight: 600;
`;

const NavButtons = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
`;

const NavButton = styled.button`
  padding: 10px 20px;
  border: 1px solid #dee2e6;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;

  &:disabled {
    opacity: 0.4;
    cursor: default;
  }
`;

const QuestionNav = styled.span`
  font-size: 14px;
  color: #868e96;
`;

const SubmitButton = styled.button`
  padding: 10px 20px;
  background: #e03131;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
`;

const QuestionGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 6px;
  margin-top: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
`;

const GridItem = styled.button<{ $answered: boolean; $current: boolean }>`
  width: 100%;
  aspect-ratio: 1;
  border: 2px solid ${(p) => (p.$current ? '#1971c2' : p.$answered ? '#40c057' : '#dee2e6')};
  background: ${(p) => (p.$current ? '#e7f5ff' : p.$answered ? '#d3f9d8' : '#fff')};
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: #333;
`;

const ResultSection = styled.div`
  text-align: center;
  padding: 40px 0;
`;

const ResultTitle = styled.h2`
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 24px;
`;

const ScoreBox = styled.div`
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
`;

const ScoreNum = styled.span`
  font-size: 64px;
  font-weight: 800;
  color: #1971c2;
`;

const ScoreDivider = styled.span`
  font-size: 32px;
  color: #adb5bd;
`;

const ScoreTotal = styled.span`
  font-size: 32px;
  color: #868e96;
`;

const ScorePercent = styled.div`
  font-size: 18px;
  color: #495057;
  margin-top: 8px;
`;

const GradeInfo = styled.div`
  font-size: 22px;
  font-weight: 700;
  color: #2b8a3e;
  margin-top: 16px;
`;

const ResultButtons = styled.div`
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 32px;
`;

const ResultButton = styled.button`
  padding: 12px 24px;
  border: 1px solid #dee2e6;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;

  &:hover {
    background: #f8f9fa;
  }
`;
