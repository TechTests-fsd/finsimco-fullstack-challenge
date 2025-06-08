import React from 'react';

interface SliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  className?: string;
}

const Slider: React.FC<SliderProps> = ({
  value,
  onChange,
  min = 1,
  max = 5,
  step = 1,
  disabled = false,
  className = ''
}) => {
    // Tailwind can't directly style pseudo-elements like ::-webkit-slider-thumb,
    // so we need this custom CSS block to style the slider's handle.
  const thumbStyle = `
    .custom-slider::-webkit-slider-thumb {
      appearance: none;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #594ede;
      cursor: pointer;
      border: 3px solid white;
      margin-top: -6px;
    }
    
    .custom-slider::-moz-range-thumb {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #594ede;
      cursor: pointer;
      border: 3px solid white;
    }
  `;

  return (
    <div className="w-full">
      <style dangerouslySetInnerHTML={{ __html: thumbStyle }} />
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className={`
          w-full h-2 
          bg-gray-200 
          rounded-full 
          appearance-none 
          focus:outline-none 
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          custom-slider
          ${className}
        `}
      />
    </div>
  );
};

export default Slider; 