import React, { useState, useRef } from 'react';

interface SliderProps {
  min?: number;
  max?: number;
  step?: number;
  value?: number;
  defaultValue?: number;
  onChange?: (value: number) => void;
  label?: string;
  className?: string;
  showValue?: boolean;
}

const Slider: React.FC<SliderProps> = ({
  min = 0,
  max = 100,
  step = 1,
  value,
  defaultValue = 50,
  onChange,
  label,
  className = '',
  showValue = true
}) => {
  const [internalValue, setInternalValue] = useState(value ?? defaultValue);
  const sliderRef = useRef<HTMLInputElement>(null);

  const currentValue = value ?? internalValue;
  const percentage = ((currentValue - min) / (max - min)) * 100;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-300">{label}</label>
          {showValue && (
            <span className="text-sm text-yellow-400 font-mono">
              {currentValue.toFixed(step < 1 ? 2 : 0)}
            </span>
          )}
        </div>
      )}
      
      <div className="relative">
        <input
          ref={sliderRef}
          type="range"
          min={min}
          max={max}
          step={step}
          value={currentValue}
          onChange={handleChange}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #facc15 0%, #facc15 ${percentage}%, #374151 ${percentage}%, #374151 100%)`
          }}
        />
        
        <style>{`
          .slider::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #facc15;
            cursor: pointer;
            border: 2px solid #1f2937;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
          }
          
          .slider::-webkit-slider-thumb:hover {
            background: #fbbf24;
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
          }
          
          .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #facc15;
            cursor: pointer;
            border: 2px solid #1f2937;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
          }
          
          .slider::-moz-range-thumb:hover {
            background: #fbbf24;
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
          }
        `}</style>
      </div>
    </div>
  );
};

export default Slider;
