import React from 'react';

interface CustomIconProps {
  src: string;
  alt: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const CustomIcon: React.FC<CustomIconProps> = ({ 
  src, 
  alt, 
  className = '', 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <img 
      src={src} 
      alt={alt} 
      className={`${sizeClasses[size]} ${className}`}
    />
  );
};

export default CustomIcon; 