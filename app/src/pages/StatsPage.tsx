import styled from 'styled-components';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { useStudyStore } from '../store/useStudyStore';

export default function StatsPage() {
  const { getTotalStats, getDailyStats, getWrongAnswers } = useStudyStore();
  const total = getTotalStats();
  const dailyStats = getDailyStats();
  const wrongAnswers = getWrongAnswers();

  // 시대별 오답 분포
  const eraDistribution: Record<string, number> = {};
  for (const wa of wrongAnswers) {
    const era = wa.question.era || '미분류';
    eraDistribution[era] = (eraDistribution[era] || 0) + 1;
  }
  const eraChartData = Object.entries(eraDistribution)
    .map(([era, count]) => ({ era, count }))
    .sort((a, b) => b.count - a.count);

  // 일별 정답률 차트 데이터
  const dailyChartData = dailyStats.slice(-30).map((d) => ({
    date: d.date.slice(5), // MM-DD
    accuracy:
      d.totalAnswered > 0
        ? Math.round((d.correctCount / d.totalAnswered) * 100)
        : 0,
    total: d.totalAnswered,
  }));

  if (total.totalAnswered === 0) {
    return (
      <Container>
        <EmptyState>
          <EmptyTitle>아직 학습 기록이 없습니다</EmptyTitle>
          <EmptyDesc>문제를 풀면 여기에 통계가 표시됩니다</EmptyDesc>
        </EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <PageTitle>학습 통계</PageTitle>

      <StatCards>
        <StatCard>
          <StatValue>{total.totalAnswered}</StatValue>
          <StatLabel>총 풀이 수</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{total.accuracy.toFixed(1)}%</StatValue>
          <StatLabel>전체 정답률</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{total.streak}일</StatValue>
          <StatLabel>연속 학습</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{wrongAnswers.length}</StatValue>
          <StatLabel>오답 문제</StatLabel>
        </StatCard>
      </StatCards>

      {dailyChartData.length > 0 && (
        <ChartSection>
          <ChartTitle>일별 정답률 (최근 30일)</ChartTitle>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={dailyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" fontSize={12} />
              <YAxis domain={[0, 100]} fontSize={12} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="accuracy"
                stroke="#1971c2"
                strokeWidth={2}
                name="정답률(%)"
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartSection>
      )}

      {eraChartData.length > 0 && (
        <ChartSection>
          <ChartTitle>시대별 오답 분포</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={eraChartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" fontSize={12} />
              <YAxis dataKey="era" type="category" fontSize={12} width={80} />
              <Tooltip />
              <Bar dataKey="count" fill="#e03131" name="오답 수" />
            </BarChart>
          </ResponsiveContainer>
        </ChartSection>
      )}
    </Container>
  );
}

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 0;
`;

const EmptyTitle = styled.h2`
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 8px;
`;

const EmptyDesc = styled.p`
  color: #868e96;
`;

const PageTitle = styled.h1`
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 24px;
`;

const StatCards = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 32px;
`;

const StatCard = styled.div`
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
`;

const StatValue = styled.div`
  font-size: 28px;
  font-weight: 800;
  color: #1971c2;
`;

const StatLabel = styled.div`
  font-size: 13px;
  color: #868e96;
  margin-top: 4px;
`;

const ChartSection = styled.section`
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
`;

const ChartTitle = styled.h3`
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 16px;
`;
