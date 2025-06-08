import { useEffect } from 'react';
import useSimulationStore from '../store/simulationStore';
import { formatTime } from '../utils/calculations';

export const useTimer = () => {
  const { timer, incrementTimer } = useSimulationStore();

  useEffect(() => {
    const interval = setInterval(() => {
      incrementTimer();
    }, 1000);

    return () => clearInterval(interval);
  }, [incrementTimer]);

  return {
    timer,
    formattedTime: formatTime(timer.totalSeconds)
  };
}; 