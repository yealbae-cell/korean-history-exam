import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import type { ExamIndex } from '../types';
import { fetchExamIndex } from '../utils/data';

export default function HomePage() {
  const [examIndex, setExamIndex] = useState<ExamIndex | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchExamIndex()
      .then(setExamIndex)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Container><Loading>로딩 중...</Loading></Container>;
  if (!examIndex) return <Container><Loading>데이터를 불러올 수 없습니다.</Loading></Container>;

  const startMockExam = () => {
    navigate('/mock-exam');
  };

  return (
    <Container>
      <Hero>
        <HeroTitle>한국사능력검정시험 기출마스터</HeroTitle>
        <HeroDesc>심화과정 기출문제로 완벽하게 대비하세요</HeroDesc>
        <MockExamButton onClick={startMockExam}>
          랜덤 모의고사 시작
        </MockExamButton>
      </Hero>

      <Section>
        <SectionTitle>기출문제 회차 목록</SectionTitle>
        <ExamGrid>
          {examIndex.exams.map((exam) => (
            <ExamCard
              key={exam.examId}
              onClick={() => navigate(`/exam/${exam.examId}`)}
            >
              <ExamRound>제{exam.round}회</ExamRound>
              <ExamYear>{exam.year}년</ExamYear>
              <ExamInfo>{exam.totalQuestions}문항</ExamInfo>
              {exam.date && <ExamDate>{exam.date}</ExamDate>}
            </ExamCard>
          ))}
        </ExamGrid>
      </Section>
    </Container>
  );
}

const Container = styled.div`
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
`;

const Loading = styled.div`
  text-align: center;
  padding: 60px 0;
  color: #888;
  font-size: 16px;
`;

const Hero = styled.div`
  text-align: center;
  padding: 48px 24px;
  background: linear-gradient(135deg, #1971c2, #1098ad);
  border-radius: 16px;
  color: #fff;
  margin-bottom: 32px;
`;

const HeroTitle = styled.h1`
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 8px;
`;

const HeroDesc = styled.p`
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 24px;
`;

const MockExamButton = styled.button`
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 700;
  background: #fff;
  color: #1971c2;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.1s;

  &:hover {
    transform: scale(1.03);
  }
`;

const Section = styled.section`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h2`
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 16px;
  color: #333;
`;

const ExamGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
`;

const ExamCard = styled.div`
  padding: 20px;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;

  &:hover {
    border-color: #339af0;
    box-shadow: 0 4px 12px rgba(51, 154, 240, 0.15);
    transform: translateY(-2px);
  }
`;

const ExamRound = styled.div`
  font-size: 20px;
  font-weight: 800;
  color: #1971c2;
`;

const ExamYear = styled.div`
  font-size: 14px;
  color: #666;
  margin-top: 4px;
`;

const ExamInfo = styled.div`
  font-size: 13px;
  color: #888;
  margin-top: 4px;
`;

const ExamDate = styled.div`
  font-size: 12px;
  color: #aaa;
  margin-top: 4px;
`;
