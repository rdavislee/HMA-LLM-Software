import { useEffect, useState, useRef } from 'react';

interface SyntaxHighlightedEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: string;
  placeholder?: string;
}

// HTML escape function
const escapeHtml = (text: string): string => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

// Language-specific keywords
const LANGUAGE_KEYWORDS: Record<string, string[]> = {
  typescript: [
    'import', 'export', 'from', 'interface', 'type', 'class', 'function', 'const', 'let', 'var',
    'if', 'else', 'for', 'while', 'return', 'extends', 'implements', 'public', 'private', 'protected',
    'static', 'async', 'await', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'super',
    'null', 'undefined', 'true', 'false', 'as', 'in', 'of', 'typeof', 'instanceof',
    'break', 'continue', 'switch', 'case', 'default', 'do', 'with', 'enum', 'namespace'
  ],
  javascript: [
    'import', 'export', 'from', 'class', 'function', 'const', 'let', 'var',
    'if', 'else', 'for', 'while', 'return', 'extends', 'async', 'await',
    'try', 'catch', 'finally', 'throw', 'new', 'this', 'super',
    'null', 'undefined', 'true', 'false', 'in', 'of', 'typeof', 'instanceof',
    'break', 'continue', 'switch', 'case', 'default', 'do', 'with'
  ],
  python: [
    'import', 'from', 'class', 'def', 'if', 'elif', 'else', 'for', 'while', 'return',
    'try', 'except', 'finally', 'raise', 'pass', 'break', 'continue', 'lambda',
    'with', 'as', 'yield', 'assert', 'del', 'global', 'nonlocal', 'in', 'is', 'not',
    'and', 'or', 'None', 'True', 'False', 'self', 'async', 'await'
  ],
  java: [
    'import', 'package', 'class', 'interface', 'extends', 'implements', 'public', 'private',
    'protected', 'static', 'final', 'abstract', 'void', 'int', 'long', 'float', 'double',
    'boolean', 'char', 'byte', 'short', 'if', 'else', 'for', 'while', 'return', 'switch',
    'case', 'default', 'break', 'continue', 'try', 'catch', 'finally', 'throw', 'throws',
    'new', 'this', 'super', 'null', 'true', 'false', 'instanceof', 'synchronized', 'volatile'
  ]
};

const highlightCode = (code: string, language: string): string => {
  if (!code) return '';
  
  // First, escape HTML to prevent XSS and rendering issues
  let highlighted = escapeHtml(code);
  
  // Get keywords for the language, fallback to typescript
  const keywords = LANGUAGE_KEYWORDS[language] || LANGUAGE_KEYWORDS.typescript || [];
  
  // Create a map to store replacements
  const replacements: Array<{ start: number; end: number; replacement: string }> = [];
  
  // Helper to add a replacement
  const addReplacement = (start: number, end: number, replacement: string) => {
    replacements.push({ start, end, replacement });
  };
  
  // 1. Find all comments (single line and multi-line)
  const commentRegex = /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)/g;
  let match: RegExpExecArray | null;
  while ((match = commentRegex.exec(highlighted)) !== null) {
    addReplacement(
      match.index,
      match.index + match[0].length,
      `<span class="syntax-comment">${match[0]}</span>`
    );
  }
  
  // 2. Find all strings (single, double, and template literals)
  const stringRegex = /(["'`])(?:(?=(\\?))\2[\s\S])*?\1/g;
  while ((match = stringRegex.exec(highlighted)) !== null) {
    // Skip if inside a comment
    const isInComment = replacements.some(r => 
      match!.index >= r.start && match!.index < r.end
    );
    if (!isInComment) {
      addReplacement(
        match.index,
        match.index + match[0].length,
        `<span class="syntax-string">${match[0]}</span>`
      );
    }
  }
  
  // 3. Find all numbers
  const numberRegex = /\b(\d+\.?\d*)\b/g;
  while ((match = numberRegex.exec(highlighted)) !== null) {
    // Skip if inside a comment or string
    const isInOther = replacements.some(r => 
      match!.index >= r.start && match!.index < r.end
    );
    if (!isInOther) {
      addReplacement(
        match.index,
        match.index + match[0].length,
        `<span class="syntax-number">${match[0]}</span>`
      );
    }
  }
  
  // 4. Find all keywords
  const keywordRegex = new RegExp(`\\b(${keywords.join('|')})\\b`, 'g');
  while ((match = keywordRegex.exec(highlighted)) !== null) {
    // Skip if inside a comment, string, or number
    const isInOther = replacements.some(r => 
      match!.index >= r.start && match!.index < r.end
    );
    if (!isInOther) {
      addReplacement(
        match.index,
        match.index + match[0].length,
        `<span class="syntax-keyword">${match[0]}</span>`
      );
    }
  }
  
  // 5. Find function names (word followed by parenthesis)
  const functionRegex = /\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?=\()/g;
  while ((match = functionRegex.exec(highlighted)) !== null) {
    // Skip if inside other syntax or if it's a keyword
    const isInOther = replacements.some(r => 
      match!.index >= r.start && match!.index < r.end
    );
    const isKeyword = match[1] && keywords.includes(match[1]);
    if (!isInOther && !isKeyword && match[1]) {
      addReplacement(
        match.index,
        match.index + match[1].length,
        `<span class="syntax-function">${match[1]}</span>`
      );
    }
  }
  
  // 6. Find types/classes (capitalized words not followed by parenthesis)
  const typeRegex = /\b([A-Z][a-zA-Z0-9_]*)\b(?!\s*\()/g;
  while ((match = typeRegex.exec(highlighted)) !== null) {
    // Skip if inside other syntax
    const isInOther = replacements.some(r => 
      match!.index >= r.start && match!.index < r.end
    );
    if (!isInOther) {
      addReplacement(
        match.index,
        match.index + match[0].length,
        `<span class="syntax-type">${match[0]}</span>`
      );
    }
  }
  
  // Sort replacements by start position (reverse order for processing)
  replacements.sort((a, b) => b.start - a.start);
  
  // Apply replacements
  for (const { start, end, replacement } of replacements) {
    highlighted = highlighted.substring(0, start) + replacement + highlighted.substring(end);
  }
  
  return highlighted;
};

export function SyntaxHighlightedEditor({
  value,
  onChange,
  language,
  placeholder = "Start typing your code here..."
}: SyntaxHighlightedEditorProps) {
  const [highlightedCode, setHighlightedCode] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlightedRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (value) {
      setHighlightedCode(highlightCode(value, language));
    } else {
      setHighlightedCode('');
    }
  }, [value, language]);

  const handleScroll = () => {
    if (textareaRef.current && highlightedRef.current) {
      highlightedRef.current.scrollTop = textareaRef.current.scrollTop;
      highlightedRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      // Insert 4 spaces for tab
      const newValue = value.substring(0, start) + '    ' + value.substring(end);
      onChange(newValue);
      
      // Set cursor position after the inserted spaces
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }
  };

  return (
    <div className="relative h-full w-full overflow-hidden bg-[#1e1e1e]">
      {/* Syntax highlighted background */}
      <div 
        ref={highlightedRef}
        className="absolute inset-0 overflow-auto pointer-events-none syntax-highlighted-content"
        style={{
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '12px',
          lineHeight: '1.6',
          padding: '1rem',
          color: '#d4d4d4',
        }}
      >
        <pre 
          style={{ 
            margin: 0, 
            padding: 0, 
            background: 'transparent',
            fontFamily: 'inherit',
            fontSize: 'inherit',
            lineHeight: 'inherit',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            overflowWrap: 'break-word'
          }}
          dangerouslySetInnerHTML={{ __html: highlightedCode || '&nbsp;' }}
        />
      </div>
      
      {/* Transparent textarea for input */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleInput}
        onScroll={handleScroll}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="absolute inset-0 w-full h-full resize-none bg-transparent border-0 outline-none code-editor-textarea"
        style={{
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '12px',
          lineHeight: '1.6',
          padding: '1rem',
          color: 'transparent',
          caretColor: '#d4d4d4',
          WebkitTextFillColor: 'transparent',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          overflowWrap: 'break-word'
        }}
        spellCheck={false}
        autoCapitalize="off"
        autoComplete="off"
        autoCorrect="off"
      />
      
      {/* Placeholder text when empty */}
      {!value && (
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: '12px',
            lineHeight: '1.6',
            padding: '1rem',
            color: '#6e6e6e',
          }}
        >
          {placeholder}
        </div>
      )}
      
    </div>
  );
}