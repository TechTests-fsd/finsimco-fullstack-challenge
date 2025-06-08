import React from 'react';
import { X } from 'lucide-react';
import useSimulationStore from '../../store/simulationStore';

const VideoModal: React.FC = () => {
  const { isVideoModalOpen, closeVideoModal } = useSimulationStore();

  if (!isVideoModalOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Training Video
          </h2>
          <button
            onClick={closeVideoModal}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
          <p className="text-gray-500 text-center">
            Video placeholder - Training content would be displayed here
          </p>
        </div>
      </div>
    </div>
  );
};

export default VideoModal; 