import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import type { Exam } from '../types';
import { fetchExam } from '../utils/data';
import { useStudyStore } from '../store/useStudyStore';
import QuestionCard from '../components/QuestionCard';

export default function ExamPage() {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [showResult, setShowResult] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { recordAnswer } = useStudyStore();

  useEffect(() => {
    if (!examId) return;
    fetchExam(examId)
      .then(setExam)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [examId]);

  if (loading) return <Container><Center>로딩 중...</Center></Container>;
  if (!exam) return <Container><Center>시험 데이터를 불러올 수 없습니다.</Center></Container>;

  const questions = exam.questions;
  const current = questions[currentIdx];
  const totalAnswered = Object.keys(answers).length;

  const handleSelect = (choiceNum: number) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [current.id]: choiceNum }));
    setShowResult(true);
    recordAnswer(exam.examId, current, choiceNum);
  };

  const handleNext = () => {
    setShowResult(false);
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    }
  };

  const handlePrev = () => {
    setShowResult(false);
    if (currentIdx > 0) {
      setCurrentIdx(currentIdx - 1);
    }
  };

  const handleSubmit = () => {
    setSubmitted(true);
    setShowResult(true);
  };

  const correctCount = questions.filter(
    (q) => answers[q.id] === q.answer
  ).length;

  return (
    <Container>
      <ExamHeader>
        <BackButton onClick={() => navigate('/')}>← 목록</BackButton>
        <ExamTitle>제{exam.round}회 ({exam.year}년)</ExamTitle>
        <Progress>
          {totalAnswered}/{questions.length} 풀이
        </Progress>
      </ExamHeader>

      {submitted ? (
        <ResultSection>
          <ResultTitle>채점 결과</ResultTitle>
          <ScoreBox>
            <ScoreNum>{correctCount}</ScoreNum>
            <ScoreDivider>/</ScoreDivider>
            <ScoreTotal>{questions.length}</ScoreTotal>
          </ScoreBox>
          <ScorePercent>
            정답률 {((correctCount / questions.length) * 100).toFixed(1)}%
          </ScorePercent>
          <ResultButtons>
            <ResultButton onClick={() => navigate('/')}>홈으로</ResultButton>
            <ResultButton onClick={() => navigate('/wrong-answers')}>
              오답노트 보기
            </ResultButton>
          </ResultButtons>
        </ResultSection>
      ) : (
        <>
          <QuestionCard
            question={current}

            total={questions.length}
            selectedAnswer={answers[current.id] ?? null}
            showResult={showResult || answers[current.id] !== undefined}
            onSelect={handleSelect}
          />
          <NavButtons>
            <NavButton onClick={handlePrev} disabled={currentIdx === 0}>
              ← 이전
            </NavButton>
            <QuestionNav>
              {currentIdx + 1} / {questions.length}
            </QuestionNav>
            {currentIdx === questions.length - 1 ? (
              <SubmitButton onClick={handleSubmit}>
                채점하기
              </SubmitButton>
            ) : (
              <NavButton onClick={handleNext}>
                다음 →
              </NavButton>
            )}
          </NavButtons>
        </>
      )}
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

const ExamHeader = styled.div`
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
  color: #495057;

  &:hover {
    background: #f8f9fa;
  }
`;

const ExamTitle = styled.h2`
  font-size: 18px;
  font-weight: 700;
  margin: 0;
`;

const Progress = styled.span`
  font-size: 14px;
  color: #868e96;
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

  &:hover:not(:disabled) {
    background: #f8f9fa;
  }

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
  background: #1971c2;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;

  &:hover {
    background: #1864ab;
  }
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
