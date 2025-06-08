import type { SimulationData, ValuationData } from '../types/simulation';

export const MAX_VALUATION = 1000000000; 

export const calculateValuation = (data: SimulationData): ValuationData => {
  const { ebitda, multiple, factorScore } = data;
  
  const amount = ebitda * multiple * factorScore;
  
  const percentage = Math.min((amount / MAX_VALUATION) * 100, 100);
  
  return {
    amount,
    percentage,
    maxValuation: MAX_VALUATION
  };
};

export const formatCurrency = (amount: number): string => {
  if (amount >= 1000000000) {
    return `$${(amount / 1000000000).toFixed(1)}B`;
  } else if (amount >= 1000000) {
    return `$${(amount / 1000000).toFixed(0)} million`;
  } else if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(0)}K`;
  } else {
    return `$${amount.toFixed(0)}`;
  }
};

export const formatTime = (totalSeconds: number): string => {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  
  const pad = (num: number): string => num.toString().padStart(2, '0');
  
  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}; 