import { useState, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Send, Paperclip, X, File, Loader2 } from 'lucide-react';

interface AttachedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  content?: string;
}

interface UserInputProps {
  onSendMessage: (message: string, files?: AttachedFile[]) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function UserInput({ 
  onSendMessage, 
  isLoading = false,
  disabled = false,
  placeholder = "Enter a prompt"
}: UserInputProps) {
  const [inputMessage, setInputMessage] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = () => {
    if (inputMessage.trim() || attachedFiles.length > 0) {
      onSendMessage(inputMessage, attachedFiles);
      setInputMessage('');
      setAttachedFiles([]);
    }
  };

  const handleFileSelect = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const newFiles: AttachedFile[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileId = `file-${Date.now()}-${i}`;
      
      // Read file content for text files
      if (file?.type.startsWith('text/') || file?.name.endsWith('.md') || file?.name.endsWith('.json')) {
        const content = await file.text();
        newFiles.push({
          id: fileId,
          name: file?.name || 'unknown',
          size: file?.size || 0,
          type: file?.type || 'text/plain',
          content
        });
      } else {
        newFiles.push({
          id: fileId,
          name: file?.name || 'unknown',
          size: file?.size || 0,
          type: file?.type || 'application/octet-stream'
        });
      }
    }
    
    setAttachedFiles(prev => [...prev, ...newFiles]);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  const removeFile = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="relative h-full flex flex-col">
      {/* Attached files display */}
      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 border-b border-border">
          {attachedFiles.map(file => (
            <div 
              key={file.id}
              className="flex items-center gap-2 px-3 py-1 bg-muted/50 rounded-md text-sm"
            >
              <File className="h-3 w-3 text-muted-foreground" />
              <span className="text-foreground">{file.name}</span>
              <span className="text-xs text-muted-foreground">
                ({formatFileSize(file.size)})
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-4 w-4 p-0 hover:bg-transparent"
                onClick={() => removeFile(file.id)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
      
      {/* Input area */}
      <div className="minimalist-input flex-1 relative">
        <textarea
          placeholder={placeholder}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && !disabled && !isLoading) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          className="w-full h-full bg-transparent resize-none text-foreground placeholder-muted-foreground focus:outline-none text-body leading-relaxed pr-24"
          style={{ border: 'none' }}
          disabled={disabled || isLoading}
        />
        
        {/* Action buttons */}
        <div className="absolute top-4 right-4 flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="p-2 hover:bg-muted/50"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || isLoading}
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          
          <Button 
            onClick={handleSendMessage} 
            className="minimalist-button p-2"
            disabled={(!inputMessage.trim() && attachedFiles.length === 0) || disabled || isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept="text/*,.md,.json,.js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.h,.cs,.go,.rb,.php,.html,.css,.xml,.yaml,.yml"
        />
      </div>
    </div>
  );
}