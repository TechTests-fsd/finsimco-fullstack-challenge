import React from 'react';
import { useTimer } from '../../hooks/useTimer';
import useSimulationStore from '../../store/simulationStore';

const Header: React.FC = () => {
  const { formattedTime } = useTimer();
  const { user } = useSimulationStore();

  return (
    <div className="w-full bg-gray-100">
      <header className="px-8 py-4 flex items-center justify-between max-w-[1400px] mx-auto relative left-0">
        <div className="flex items-center gap-6">
          <div className="bg-white px-4 py-2 rounded-md text-gray-800 text-sm font-medium">
            Timer: {formattedTime}
          </div>
          
          <div className="flex items-center gap-4">
            <div className="bg-white px-4 py-2 rounded-md text-gray-800 text-sm font-medium">
              Stage: ANALYSIS
            </div>
            <div className="bg-white px-4 py-2 rounded-md text-gray-800 text-sm font-medium">
              Next Stage: STRUCTURING - 1 hour
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4 ml-auto">
          <span className="text-base font-semibold text-gray-800">
            {user.name}
          </span>
          <button 
            className="text-accent-purple text-sm border-none bg-transparent cursor-pointer px-2 py-1 rounded transition-all duration-200 hover:bg-accent-purple/10"
          >
            Logout
          </button>
        </div>
      </header>
    </div>
  );
};

export default Header; 