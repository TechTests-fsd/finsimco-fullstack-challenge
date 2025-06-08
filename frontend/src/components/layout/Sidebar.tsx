import React from 'react';
import { Play, FileText } from 'lucide-react';
import useSimulationStore from '../../store/simulationStore';
import Tooltip from '../ui/Tooltip';

const Sidebar: React.FC = () => {
  const { openVideoModal, openTextModal } = useSimulationStore();

  return (
    <aside className="w-16 bg-sidebar-dark flex flex-col items-center py-6 gap-6 fixed left-0 top-0 bottom-0">
      <div className="text-accent-purple text-xl font-bold">
        Sim
      </div>

      <Tooltip content="Watch introduction video" position="right">
        <button
          onClick={openVideoModal}
          className="w-10 h-10 bg-white/10 rounded-md flex items-center justify-center border-none cursor-pointer transition-all duration-200 hover:bg-white/15"
          aria-label="Open video modal"
        >
          <Play className="w-5 h-5 text-white" />
        </button>
      </Tooltip>

      <Tooltip content="View documentation" position="right">
        <button
          onClick={openTextModal}
          className="w-10 h-10 bg-white/10 rounded-md flex items-center justify-center border-none cursor-pointer transition-all duration-200 hover:bg-white/15"
          aria-label="Open text modal"
        >
          <FileText className="w-5 h-5 text-white" />
        </button>
      </Tooltip>
    </aside>
  );
};

export default Sidebar; 