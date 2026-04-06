import styled from 'styled-components';
import type { Question } from '../types';

const DATA_BASE_URL = import.meta.env.VITE_DATA_URL || `${import.meta.env.BASE_URL}data`;

interface Props {
  question: Question;
  total: number;
  selectedAnswer: number | null;
  showResult: boolean;
  onSelect: (choiceNum: number) => void;
}

export default function QuestionCard({
  question,
  total,
  selectedAnswer,
  showResult,
  onSelect,
}: Props) {
  return (
    <Card>
      <QuestionNumber>
        문제 {question.id} / {total}
      </QuestionNumber>
      <QuestionText>{question.question}</QuestionText>
      {question.description && (
        <Description>{question.description}</Description>
      )}
      {question.image && <QuestionImage src={`${DATA_BASE_URL}/${question.image}`} alt="문제 이미지" />}
      <ChoiceList>
        {question.choices.map((choice) => {
          const isSelected = selectedAnswer === choice.number;
          const isCorrect = choice.number === question.answer;
          let status: 'default' | 'selected' | 'correct' | 'wrong' = 'default';
          if (showResult) {
            if (isCorrect) status = 'correct';
            else if (isSelected && !isCorrect) status = 'wrong';
          } else if (isSelected) {
            status = 'selected';
          }

          return (
            <ChoiceButton
              key={choice.number}
              $status={status}
              onClick={() => !showResult && onSelect(choice.number)}
              disabled={showResult}
            >
              <ChoiceNumber $status={status}>{choice.number}</ChoiceNumber>
              <ChoiceText>{choice.text}</ChoiceText>
            </ChoiceButton>
          );
        })}
      </ChoiceList>
      {showResult && selectedAnswer !== null && (
        <ResultBadge $correct={selectedAnswer === question.answer}>
          {selectedAnswer === question.answer ? '정답!' : `오답 (정답: ${question.answer}번)`}
        </ResultBadge>
      )}
    </Card>
  );
}

const Card = styled.div`
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  max-width: 700px;
  margin: 0 auto;
`;

const QuestionNumber = styled.div`
  font-size: 14px;
  color: #888;
  margin-bottom: 8px;
`;

const QuestionText = styled.h3`
  font-size: 18px;
  font-weight: 600;
  line-height: 1.6;
  margin: 0 0 12px;
  color: #222;
`;

const Description = styled.p`
  font-size: 15px;
  color: #555;
  line-height: 1.5;
  margin: 0 0 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
`;

const QuestionImage = styled.img`
  max-width: 100%;
  border-radius: 8px;
  margin-bottom: 16px;
`;

const ChoiceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const statusColors = {
  default: { bg: '#f8f9fa', border: '#e9ecef', text: '#333' },
  selected: { bg: '#e7f5ff', border: '#339af0', text: '#1971c2' },
  correct: { bg: '#d3f9d8', border: '#40c057', text: '#2b8a3e' },
  wrong: { bg: '#ffe3e3', border: '#fa5252', text: '#c92a2a' },
};

const ChoiceButton = styled.button<{ $status: keyof typeof statusColors }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 2px solid ${(p) => statusColors[p.$status].border};
  background: ${(p) => statusColors[p.$status].bg};
  color: ${(p) => statusColors[p.$status].text};
  border-radius: 8px;
  cursor: ${(p) => (p.disabled ? 'default' : 'pointer')};
  transition: all 0.15s;
  text-align: left;
  font-size: 15px;

  &:hover:not(:disabled) {
    border-color: #339af0;
    background: #e7f5ff;
  }
`;

const ChoiceNumber = styled.span<{ $status: keyof typeof statusColors }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: ${(p) => (p.$status === 'default' ? '#dee2e6' : statusColors[p.$status].border)};
  color: ${(p) => (p.$status === 'default' ? '#495057' : '#fff')};
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
`;

const ChoiceText = styled.span`
  line-height: 1.4;
`;

const ResultBadge = styled.div<{ $correct: boolean }>`
  margin-top: 16px;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  text-align: center;
  background: ${(p) => (p.$correct ? '#d3f9d8' : '#ffe3e3')};
  color: ${(p) => (p.$correct ? '#2b8a3e' : '#c92a2a')};
`;
