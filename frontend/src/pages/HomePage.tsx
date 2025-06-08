import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Financial Simulation
          </h1>
          <p className="text-gray-600">
            Choose your team role to begin the simulation
          </p>
        </div>
        
        <div className="space-y-4">
          <Link to="/team1" className="block">
            <Button 
              variant="primary" 
              size="lg" 
              className="w-full"
            >
              Team 1 - Input Values
            </Button>
          </Link>
          
          <Link to="/team2" className="block">
            <Button 
              variant="secondary" 
              size="lg" 
              className="w-full"
            >
              Team 2 - Review & Toggle
            </Button>
          </Link>
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Team 1 can modify input values<br />
            Team 2 can toggle TBD/OK status
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 