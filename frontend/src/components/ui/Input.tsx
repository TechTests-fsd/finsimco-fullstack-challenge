import React from 'react';

interface InputProps {
  value: string | number;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'number';
  disabled?: boolean;
  className?: string;
  label?: string;
  required?: boolean;
}

const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  type = 'text',
  disabled = false,
  className = '',
  label,
  required = false
}) => {
  const inputClasses = `
    w-full px-4 py-3 
    border border-gray-300 
    rounded-md
    text-base
    ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white text-gray-900 cursor-text'}
    focus:border-indigo-500 focus:outline-none
    transition-colors
    ${className}
  `;

  const labelClasses = "block text-sm font-medium text-gray-700 mb-2";

  return (
    <div className="w-full">
      {label && (
        <label className={labelClasses}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={inputClasses}
      />
    </div>
  );
};

export default Input; 