import { useState, useRef, useEffect } from 'react';
import { Input } from './ui/input';

interface EditableProjectTitleProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
  maxLength?: number;
}

export function EditableProjectTitle({ value, onChange, className, maxLength = 30 }: EditableProjectTitleProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditValue(value);
  }, [value]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSave = () => {
    const trimmedValue = editValue.trim();
    if (trimmedValue) {
      onChange(trimmedValue);
    } else {
      setEditValue(value); // Reset to previous value if empty
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  const handleBlur = () => {
    handleSave();
  };

  if (isEditing) {
    return (
      <Input
        ref={inputRef}
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        maxLength={maxLength}
        className={`text-center bg-background border-primary/20 focus:border-primary ${className}`}
        style={{
          fontFamily: 'Quicksand, sans-serif',
          fontSize: '18px',
          fontWeight: 500,
          maxWidth: '300px',
        }}
      />
    );
  }

  return (
    <button
      onClick={() => setIsEditing(true)}
      className={`px-4 py-2 rounded-md bg-background hover:bg-accent/5 border border-border hover:border-accent/20 transition-all cursor-pointer ${className}`}
      style={{
        fontFamily: 'Quicksand, sans-serif',
        fontSize: '18px',
        fontWeight: 500,
        minWidth: '200px',
        maxWidth: '300px',
      }}
      title="Click to edit project name"
    >
      <span className="truncate block" style={{ fontFamily: 'Quicksand, sans-serif' }}>{value}</span>
    </button>
  );
}