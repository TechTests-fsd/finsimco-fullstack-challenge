import React from 'react';
import useSimulationStore from '../../store/simulationStore';

const ValuationChart: React.FC = () => {
  const { valuation } = useSimulationStore();
  
  const percentage = Math.min(valuation.percentage, 100);
  const strokeDasharray = `${percentage * 2.83} 283`; 

  return (
    <div className="relative w-[250px] h-[250px]">
      <svg
        className="w-full h-full -rotate-90"
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="#e6e7eb"
          strokeWidth="12"
        />
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="#594ede"
          strokeWidth="12"
          strokeDasharray={strokeDasharray}
          className="transition-all duration-500 ease-in-out"
        />
      </svg>
      
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-[32px] font-semibold text-gray-800">
          {percentage.toFixed(0)}%
        </span>
      </div>
    </div>
  );
};

export default ValuationChart; 