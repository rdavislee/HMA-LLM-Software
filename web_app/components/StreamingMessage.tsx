import { useEffect, useState } from 'react';
import { useLLM } from '../contexts/LLMContext';
import { Loader2 } from 'lucide-react';
import { cn } from './ui/utils';

interface StreamingMessageProps {
  messageId: string;
  agentId?: string;
  initialContent?: string;
  className?: string;
  onComplete?: (finalContent: string) => void;
}

export function StreamingMessage({ 
  messageId, 
  agentId, 
  initialContent = '', 
  className,
  onComplete 
}: StreamingMessageProps) {
  const { streamingMessages, isStreaming } = useLLM();
  const [displayContent, setDisplayContent] = useState(initialContent);
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    // Update content from streaming
    const streamedContent = streamingMessages[messageId];
    if (streamedContent) {
      setDisplayContent(streamedContent);
    }
  }, [streamingMessages, messageId]);

  useEffect(() => {
    // Check if streaming is complete
    const stillStreaming = isStreaming[messageId];
    if (stillStreaming === false && displayContent && isTyping) {
      setIsTyping(false);
      onComplete?.(displayContent);
    }
  }, [isStreaming, messageId, displayContent, isTyping, onComplete]);

  return (
    <div className={cn("relative", className)}>
      <div className="prose prose-sm dark:prose-invert max-w-none">
        {displayContent || (
          <span className="text-muted-foreground italic">Thinking...</span>
        )}
      </div>
      
      {isTyping && (
        <div className="absolute -bottom-6 left-0 flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="h-3 w-3 animate-spin" />
          <span>
            {agentId ? `${agentId.split('/').pop()} is typing...` : 'Generating response...'}
          </span>
        </div>
      )}
      
      {/* Typing indicator animation */}
      {isTyping && displayContent && (
        <span className="inline-block w-1 h-4 bg-primary animate-pulse ml-0.5" />
      )}
    </div>
  );
}