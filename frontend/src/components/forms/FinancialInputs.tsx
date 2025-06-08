import React from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import InputField from './InputField';
import ValuationChart from '../charts/ValuationChart';
import useSimulationStore from '../../store/simulationStore';
import { formatCurrency } from '../../utils/calculations';

const FinancialInputs: React.FC = () => {
  const {
    isFirstTimeGuidanceOpen,
    toggleFirstTimeGuidance,
    simulation,
    valuation
  } = useSimulationStore();

  return (
    <div className="max-w-[1400px] mx-auto">
      <div className="bg-white rounded-md p-8 flex flex-col gap-8">
        <div className="bg-gray-50 rounded-md border border-gray-200">
          <button
            onClick={toggleFirstTimeGuidance}
            className="w-full flex items-center justify-between p-5 text-left bg-transparent border-none cursor-pointer"
          >
            <h2 className="text-base font-semibold text-gray-800 m-0">
              First Time Guidance
            </h2>
            {isFirstTimeGuidanceOpen ? (
              <ChevronUp className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            )}
          </button>
          
          {isFirstTimeGuidanceOpen && (
            <div className="px-6 pb-6 border-t border-gray-200">
              <p className="text-gray-600 leading-relaxed mt-4 text-sm">
                This is the first time guidance text. It can contain up to 500 characters. This section provides important information to help you understand the simulation and its objectives. Please read it carefully. This message will only be expanded by default the first time you use the application.
              </p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-8">
          <div>
            <div className="flex flex-col gap-6">
              <InputField
                field="ebitda"
                label="EBITDA"
                type="number"
                placeholder=""
              />
              
              <InputField
                field="interestRate"
                label="Interest Rate (%)"
                type="number"
                placeholder=""
              />
              
              <InputField
                field="multiple"
                label="Multiple"
                type="number"
                placeholder=""
              />
              
              <InputField
                field="factorScore"
                label={`Factor Score: ${simulation.factorScore}`}
                type="slider"
                min={1}
                max={5}
              />
              
              <InputField
                field="companyName"
                label="Company Name"
                type="text"
                placeholder=""
              />
              
              <InputField
                field="description"
                label="Description"
                type="textarea"
                placeholder=""
              />
              
              <div className="flex justify-center mt-4">
                <button className="bg-accent-purple text-white px-12 py-4 rounded-md font-semibold text-base border-none cursor-pointer transition-all duration-200 min-w-[200px] hover:bg-indigo-600">
                  SUBMIT
                </button>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-md p-8 flex flex-col items-center gap-4">
            <div className="text-sm font-medium text-gray-400 uppercase -mb-2">
              Valuation
            </div>
            <div className="text-3xl font-semibold text-accent-purple mb-2">
              {formatCurrency(valuation.amount)}
            </div>
            <ValuationChart />
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialInputs; 