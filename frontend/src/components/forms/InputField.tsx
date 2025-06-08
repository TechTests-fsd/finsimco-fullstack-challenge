import React from 'react';
import Input from '../ui/Input';
import Slider from '../ui/Slider';
import Button from '../ui/Button';
import useSimulationStore from '../../store/simulationStore';
import type { SimulationField, FieldToggleStatus } from '../../types/simulation';

interface InputFieldProps {
  field: SimulationField;
  label: string;
  type?: 'text' | 'number' | 'slider' | 'textarea';
  placeholder?: string;
  min?: number;
  max?: number;
}

const InputField: React.FC<InputFieldProps> = ({
  field,
  label,
  type = 'text',
  placeholder,
  min,
  max
}) => {
  const {
    simulation,
    fieldStatus,
    updateSimulationField,
    updateFieldStatus,
    user
  } = useSimulationStore();
  
  const value = simulation[field];
  const status = fieldStatus[field];
  const isTeam1 = user.role === 'team1';
  const isTeam2 = user.role === 'team2';

  const handleValueChange = (newValue: string | number) => {
    if (!isTeam1) return; 
    updateSimulationField(field, newValue);
  };

  const handleStatusToggle = (newStatus: FieldToggleStatus) => {
    if (!isTeam2) return; 
    updateFieldStatus(field, newStatus);
  };

  const renderInput = () => {
    if (type === 'slider') {
      return (
        <Slider
          value={value as number}
          onChange={handleValueChange}
          min={min}
          max={max}
          disabled={!isTeam1}
        />
      );
    }
    
    if (type === 'textarea') {
      return (
        <textarea
          value={value as string}
          onChange={(e) => handleValueChange(e.target.value)}
          placeholder={placeholder}
          disabled={!isTeam1}
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-md text-base bg-white focus:border-indigo-500 focus:outline-none disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed resize-none font-sans"
        />
      );
    }

    return (
      <Input
        value={value}
        onChange={handleValueChange}
        type={type}
        placeholder={placeholder}
        disabled={!isTeam1}
      />
    );
  };

  return (
    <div className="flex items-end gap-6">
      <div className="flex-1 flex flex-col gap-3">
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
        {renderInput()}
      </div>
      
      <div className="flex items-end gap-3">
        <Button
          variant="toggle"
          size="md"
          active={status === 'TBD'}
          onClick={() => handleStatusToggle('TBD')}
          disabled={!isTeam2}
          className="min-w-[60px]"
        >
          TBD
        </Button>
        <Button
          variant="toggle"
          size="md"
          active={status === 'OK'}
          onClick={() => handleStatusToggle('OK')}
          disabled={!isTeam2}
          className="min-w-[60px]"
        >
          OK
        </Button>
      </div>
    </div>
  );
};

export default InputField; 