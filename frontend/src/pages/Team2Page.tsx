import React, { useEffect } from 'react';
import Layout from '../components/layout/Layout';
import FinancialInputs from '../components/forms/FinancialInputs';
import VideoModal from '../components/modals/VideoModal';
import TextModal from '../components/modals/TextModal';
import useSimulationStore from '../store/simulationStore';

const Team2Page: React.FC = () => {
  const { setUserRole } = useSimulationStore();

  useEffect(() => {
    setUserRole('team2');
  }, [setUserRole]);

  return (
    <div>
      <Layout>
        <FinancialInputs />
      </Layout>
      
      <VideoModal />
      <TextModal />
    </div>
  );
};

export default Team2Page; 