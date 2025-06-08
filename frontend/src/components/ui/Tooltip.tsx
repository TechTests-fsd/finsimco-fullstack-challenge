import React, { useState } from 'react';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'right' | 'bottom' | 'left';
}

const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'right'
}) => {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2'
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div 
          className={`absolute z-10 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-md shadow-sm whitespace-nowrap ${positionClasses[position]}`}
          role="tooltip"
        >
          {content}
          <div 
            className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
              position === 'top' ? 'top-full -translate-y-1/2' : 
              position === 'right' ? 'right-full translate-x-1/2' : 
              position === 'bottom' ? 'bottom-full translate-y-1/2' : 
              'left-full -translate-x-1/2'
            }`}
          />
        </div>
      )}
    </div>
  );
};

export default Tooltip; 