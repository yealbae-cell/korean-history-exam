import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useStudyStore } from '../store/useStudyStore';
import QuestionCard from '../components/QuestionCard';

export default function WrongAnswersPage() {
  const navigate = useNavigate();
  const { getWrongAnswers, recordAnswer } = useStudyStore();
  const wrongAnswers = getWrongAnswers();
  const [currentIdx, setCurrentIdx] = useState(0);
  const [retryAnswers, setRetryAnswers] = useState<Record<string, number>>({});
  const [showResults, setShowResults] = useState<Record<string, boolean>>({});
  const [mode, setMode] = useState<'list' | 'retry'>('list');

  if (wrongAnswers.length === 0) {
    return (
      <Container>
        <EmptyState>
          <EmptyIcon>✓</EmptyIcon>
          <EmptyTitle>오답이 없습니다!</EmptyTitle>
          <EmptyDesc>기출문제를 풀어보세요</EmptyDesc>
          <GoButton onClick={() => navigate('/')}>문제 풀러 가기</GoButton>
        </EmptyState>
      </Container>
    );
  }

  if (mode === 'retry') {
    const current = wrongAnswers[currentIdx];
    const key = `${current.examId}-${current.questionId}`;

    const handleSelect = (choiceNum: number) => {
      setRetryAnswers((prev) => ({ ...prev, [key]: choiceNum }));
      setShowResults((prev) => ({ ...prev, [key]: true }));
      recordAnswer(current.examId, current.question, choiceNum);
    };

    return (
      <Container>
        <PageHeader>
          <BackButton onClick={() => setMode('list')}>← 목록</BackButton>
          <PageTitle>오답 다시 풀기</PageTitle>
          <Progress>{currentIdx + 1}/{wrongAnswers.length}</Progress>
        </PageHeader>

        <QuestionCard
          question={current.question}

          total={wrongAnswers.length}
          selectedAnswer={retryAnswers[key] ?? null}
          showResult={showResults[key] ?? false}
          onSelect={handleSelect}
        />

        <NavButtons>
          <NavButton
            onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
            disabled={currentIdx === 0}
          >
            ← 이전
          </NavButton>
          <NavButton
            onClick={() => setCurrentIdx((i) => Math.min(wrongAnswers.length - 1, i + 1))}
            disabled={currentIdx === wrongAnswers.length - 1}
          >
            다음 →
          </NavButton>
        </NavButtons>
      </Container>
    );
  }

  return (
    <Container>
      <PageHeader>
        <PageTitle>오답노트</PageTitle>
        <RetryAllButton onClick={() => { setMode('retry'); setCurrentIdx(0); }}>
          전체 다시 풀기 ({wrongAnswers.length}문제)
        </RetryAllButton>
      </PageHeader>

      <WrongList>
        {wrongAnswers.map((wa) => (
          <WrongItem key={`${wa.examId}-${wa.questionId}`}>
            <WrongItemHeader>
              <WrongExam>{wa.examId} - {wa.questionId}번</WrongExam>
              <WrongCount>오답 {wa.wrongCount}회</WrongCount>
            </WrongItemHeader>
            <WrongQuestion>{wa.question.question}</WrongQuestion>
            <WrongMeta>
              {wa.question.category} · {wa.question.era} · 정답: {wa.question.answer}번
            </WrongMeta>
          </WrongItem>
        ))}
      </WrongList>
    </Container>
  );
}

const Container = styled.div`
  max-width: 700px;
  margin: 0 auto;
  padding: 24px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 0;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
`;

const EmptyTitle = styled.h2`
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 8px;
`;

const EmptyDesc = styled.p`
  color: #868e96;
  margin: 0 0 24px;
`;

const GoButton = styled.button`
  padding: 12px 24px;
  background: #1971c2;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
`;

const PageHeader = styled.div`
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
`;

const PageTitle = styled.h2`
  font-size: 20px;
  font-weight: 700;
  margin: 0;
`;

const Progress = styled.span`
  font-size: 14px;
  color: #868e96;
`;

const RetryAllButton = styled.button`
  padding: 8px 16px;
  background: #e03131;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
`;

const NavButtons = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
`;

const NavButton = styled.button`
  padding: 10px 20px;
  border: 1px solid #dee2e6;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;

  &:disabled {
    opacity: 0.4;
    cursor: default;
  }
`;

const WrongList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const WrongItem = styled.div`
  padding: 16px;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
`;

const WrongItemHeader = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const WrongExam = styled.span`
  font-size: 13px;
  color: #1971c2;
  font-weight: 600;
`;

const WrongCount = styled.span`
  font-size: 13px;
  color: #e03131;
  font-weight: 600;
`;

const WrongQuestion = styled.p`
  font-size: 15px;
  line-height: 1.5;
  margin: 0 0 8px;
  color: #333;
`;

const WrongMeta = styled.div`
  font-size: 12px;
  color: #868e96;
`;
