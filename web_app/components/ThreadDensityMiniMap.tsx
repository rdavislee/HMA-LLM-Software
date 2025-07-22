import { useState, useEffect, useRef, useCallback } from 'react';

interface ThreadDensityMiniMapProps {
  threads: Array<{
    taskId: string;
    messageCount: number;
    lastActivity: string;
    isCollapsed: boolean;
    messages: Array<{
      id: string;
      timestamp: string;
      sender: 'user' | 'assistant';
    }>;
  }>;
  onScrollToThread: (threadId: string) => void;
  className?: string;
}

export function ThreadDensityMiniMap({ 
  threads, 
  onScrollToThread, 
  className 
}: ThreadDensityMiniMapProps) {
  const [densityData, setDensityData] = useState<Array<{
    threadId: string;
    density: number;
    position: number;
    color: string;
  }>>([]);
  
  const miniMapRef = useRef<HTMLDivElement>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // Calculate message density for each thread
  useEffect(() => {
    const calculateDensity = () => {
      const totalMessages = threads.reduce((sum, thread) => sum + thread.messageCount, 0);
      let cumulativePosition = 0;
      
      const densities = threads.map((thread, _index) => {
        const density = totalMessages > 0 ? thread.messageCount / totalMessages : 0;
        const position = cumulativePosition / totalMessages;
        cumulativePosition += thread.messageCount;
        
        // Calculate color based on density and recent activity
        const recentActivity = new Date(thread.lastActivity).getTime();
        const now = new Date().getTime();
        const hoursSinceActivity = (now - recentActivity) / (1000 * 60 * 60);
        
        let color = '#4B5563'; // Default gray
        
        if (density > 0.3) {
          // High density - red hot
          color = '#EF4444';
        } else if (density > 0.15) {
          // Medium density - orange
          color = '#F97316';
        } else if (density > 0.05) {
          // Low density - yellow
          color = '#EAB308';
        } else if (hoursSinceActivity < 1) {
          // Very recent activity - blue
          color = '#3B82F6';
        }
        
        return {
          threadId: thread.taskId,
          density: Math.max(density, 0.02), // Minimum visibility
          position,
          color
        };
      });
      
      setDensityData(densities);
    };

    calculateDensity();
  }, [threads]);

  const handleClick = useCallback((event: React.MouseEvent, threadId: string) => {
    event.preventDefault();
    onScrollToThread(threadId);
  }, [onScrollToThread]);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (!miniMapRef.current) return;
    
    const rect = miniMapRef.current.getBoundingClientRect();
    const y = event.clientY - rect.top;
    const relativeY = y / rect.height;
    
    // Find the closest density band
    let closestIndex = -1;
    let minDistance = Infinity;
    
    densityData.forEach((item, index) => {
      const distance = Math.abs(item.position - relativeY);
      if (distance < minDistance) {
        minDistance = distance;
        closestIndex = index;
      }
    });
    
    setHoveredIndex(closestIndex);
  }, [densityData]);

  const handleMouseLeave = useCallback(() => {
    setHoveredIndex(null);
  }, []);

  return (
    <div className={`relative ${className || ''}`}>
      <div
        ref={miniMapRef}
        className="w-2 h-full bg-background/60 rounded-sm relative cursor-pointer overflow-hidden"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        {/* Density bands */}
        {densityData.map((item, index) => {
          const height = Math.max(item.density * 100, 2); // Minimum 2% height
          const top = item.position * 100;
          const isHovered = hoveredIndex === index;
          
          return (
            <div
              key={item.threadId}
              className={`absolute left-0 right-0 rounded-sm transition-all duration-200 ${
                isHovered ? 'scale-x-150 z-10' : ''
              }`}
              style={{
                top: `${top}%`,
                height: `${height}%`,
                backgroundColor: item.color,
                boxShadow: isHovered ? `0 0 8px ${item.color}` : 'none'
              }}
              onClick={(e) => handleClick(e, item.threadId)}
            />
          );
        })}
        
        {/* Hover indicator */}
        {hoveredIndex !== null && (
          <div
            className="absolute left-0 right-0 border-t border-white/50 pointer-events-none"
            style={{
              top: `${densityData[hoveredIndex]?.position ? densityData[hoveredIndex].position * 100 : 0}%`
            }}
          />
        )}
      </div>
      
      {/* Tooltip */}
      {hoveredIndex !== null && (
        <div className="absolute left-4 top-0 bg-background/90 backdrop-blur-sm border border-border/50 rounded-md p-2 text-xs whitespace-nowrap z-20">
          <div className="font-medium">
            Thread {hoveredIndex + 1}
          </div>
          <div className="text-muted-foreground">
            {densityData[hoveredIndex]?.density && densityData[hoveredIndex].density > 0.3 ? 'High' : 
             densityData[hoveredIndex]?.density && densityData[hoveredIndex].density > 0.15 ? 'Medium' : 'Low'} density
          </div>
          <div className="text-muted-foreground">
            Click to scroll
          </div>
        </div>
      )}
    </div>
  );
}