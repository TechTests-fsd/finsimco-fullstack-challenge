import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'toggle';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  active?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  active = false
}) => {
  const baseClasses = "font-medium rounded transition-colors border focus:outline-none";
  
  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-3 text-base",
    lg: "px-6 py-4 text-base"
  };

  const variantClasses = {
    primary: "bg-accent-purple text-white border-transparent hover:bg-indigo-600",
    secondary: "bg-gray-100 text-gray-700 border-transparent hover:bg-gray-200",
    'toggle': active 
      ? "bg-accent-purple text-white border-accent-purple"
      : "bg-white text-gray-500 border-gray-300 hover:bg-gray-50"
  };

  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer";

  const buttonClasses = `
    ${baseClasses}
    ${sizeClasses[size]}
    ${variantClasses[variant]}
    ${disabledClasses}
    ${className}
  `;

  return (
    <button
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {children}
    </button>
  );
};

export default Button; 