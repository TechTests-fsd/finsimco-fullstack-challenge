import React from 'react';
import { X } from 'lucide-react';
import useSimulationStore from '../../store/simulationStore';

const TextModal: React.FC = () => {
  const { isTextModalOpen, closeTextModal } = useSimulationStore();

  if (!isTextModalOpen) return null;

  const documentText = `This is a detailed documentation text that can contain up to 500 characters. This section provides comprehensive information about the simulation methodology, scoring criteria, and best practices for achieving optimal results. It includes important guidelines that participants should follow during the simulation process. This information is crucial for understanding the evaluation metrics and making informed decisions throughout the exercise.`;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Documentation
          </h2>
          <button
            onClick={closeTextModal}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 leading-relaxed">
            {documentText}
          </p>
        </div>
      </div>
    </div>
  );
};

export default TextModal; 