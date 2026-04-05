import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { createGlobalStyle } from 'styled-components';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import ExamPage from './pages/ExamPage';
import MockExamPage from './pages/MockExamPage';
import WrongAnswersPage from './pages/WrongAnswersPage';
import StatsPage from './pages/StatsPage';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR',
      sans-serif;
    background: #f1f3f5;
    color: #333;
    -webkit-font-smoothing: antialiased;
  }

  button {
    font-family: inherit;
  }
`;

function App() {
  return (
    <BrowserRouter>
      <GlobalStyle />
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/exam/:examId" element={<ExamPage />} />
        <Route path="/mock-exam" element={<MockExamPage />} />
        <Route path="/wrong-answers" element={<WrongAnswersPage />} />
        <Route path="/stats" element={<StatsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
