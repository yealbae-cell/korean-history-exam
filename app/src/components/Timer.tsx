import { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';

interface Props {
  initialMinutes: number;
  onTimeUp?: () => void;
  running: boolean;
}

export default function Timer({ initialMinutes, onTimeUp, running }: Props) {
  const [seconds, setSeconds] = useState(initialMinutes * 60);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (running && seconds > 0) {
      intervalRef.current = window.setInterval(() => {
        setSeconds((s) => {
          if (s <= 1) {
            if (intervalRef.current) clearInterval(intervalRef.current);
            onTimeUp?.();
            return 0;
          }
          return s - 1;
        });
      }, 1000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running, seconds, onTimeUp]);

  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  const isLow = seconds < 300;

  return (
    <TimerBox $low={isLow}>
      {String(min).padStart(2, '0')}:{String(sec).padStart(2, '0')}
    </TimerBox>
  );
}

const TimerBox = styled.div<{ $low: boolean }>`
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: ${(p) => (p.$low ? '#e03131' : '#333')};
  background: ${(p) => (p.$low ? '#fff5f5' : '#f8f9fa')};
  padding: 8px 16px;
  border-radius: 8px;
  text-align: center;
`;
