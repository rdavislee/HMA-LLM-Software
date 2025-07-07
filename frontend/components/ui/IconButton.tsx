import React from 'react';
import type { LucideProps } from 'lucide-react';

// The Icon prop should accept any component that takes Lucide-like props.
type LucideIconComponent = React.ComponentType<LucideProps>;

interface IconButtonProps {
  icon: LucideIconComponent;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  tooltip?: string;
  className?: string;
  children?: React.ReactNode;
}

const IconButton: React.FC<IconButtonProps> = ({
  icon: Icon,
  onClick,
  variant = 'ghost',
  size = 'md',
  disabled = false,
  loading = false,
  tooltip,
  className = '',
  children
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900';
  
  const variantClasses = {
    primary: 'bg-yellow-400 hover:bg-yellow-300 text-black focus:ring-yellow-400 shadow-lg hover:shadow-xl',
    secondary: 'bg-gray-700 hover:bg-gray-600 text-gray-100 focus:ring-gray-500 border border-gray-600',
    ghost: 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/10 focus:ring-yellow-400',
    danger: 'text-red-400 hover:text-red-300 hover:bg-red-500/10 focus:ring-red-400'
  };

  const sizeClasses = {
    sm: 'p-1.5 text-sm',
    md: 'p-2',
    lg: 'p-3 text-lg'
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const disabledClasses = disabled 
    ? 'opacity-50 cursor-not-allowed pointer-events-none' 
    : 'cursor-pointer';

  const classes = `
    ${baseClasses}
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${disabledClasses}
    ${className}
  `.trim();

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={classes}
      title={tooltip}
    >
      {loading ? (
        <div className={`animate-spin rounded-full border-2 border-current border-t-transparent ${iconSizes[size]}`} />
      ) : (
        <Icon className={iconSizes[size]} />
      )}
      {children && (
        <span className="ml-2">{children}</span>
      )}
    </button>
  );
};

export default IconButton;
