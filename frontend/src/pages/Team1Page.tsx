import React, { useEffect } from 'react';
import Layout from '../components/layout/Layout';
import FinancialInputs from '../components/forms/FinancialInputs';
import VideoModal from '../components/modals/VideoModal';
import TextModal from '../components/modals/TextModal';
import useSimulationStore from '../store/simulationStore';

const Team1Page: React.FC = () => {
  const { setUserRole } = useSimulationStore();

  useEffect(() => {
    setUserRole('team1');
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

export default Team1Page; 