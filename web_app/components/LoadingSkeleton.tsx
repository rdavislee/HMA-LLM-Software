import { Skeleton } from './ui/skeleton';

interface FileTreeSkeletonProps {
  className?: string;
}

export function FileTreeSkeleton({ className }: FileTreeSkeletonProps) {
  return (
    <div className={`p-4 space-y-2 ${className || ''}`}>
      {/* Project title skeleton */}
      <div className="flex items-center gap-2 mb-4">
        <Skeleton className="h-4 w-4 rounded" />
        <Skeleton className="h-4 w-32" />
      </div>

      {/* Root folder skeleton */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-3 rounded" />
          <Skeleton className="h-4 w-24" />
        </div>
        
        {/* Nested files */}
        <div className="ml-4 space-y-1">
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-20" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-28" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      </div>

      {/* Second folder */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-3 rounded" />
          <Skeleton className="h-4 w-32" />
        </div>
        
        <div className="ml-4 space-y-1">
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-24" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-18" />
          </div>
        </div>
      </div>

      {/* Third folder */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-3 rounded" />
          <Skeleton className="h-4 w-20" />
        </div>
        
        <div className="ml-4 space-y-1">
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-28" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-22" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-16" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded" />
            <Skeleton className="h-4 w-24" />
          </div>
        </div>
      </div>
    </div>
  );
}

interface ThreadedChatSkeletonProps {
  className?: string;
}

export function ThreadedChatSkeleton({ className }: ThreadedChatSkeletonProps) {
  return (
    <div className={`p-4 space-y-4 ${className || ''}`}>
      {/* Filter chips skeleton */}
      <div className="flex gap-2 mb-4">
        <Skeleton className="h-8 w-12" />
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-8 w-20" />
      </div>

      {/* Thread skeletons */}
      {[...Array(3)].map((_, i) => (
        <div key={i} className="border border-border/30 rounded-lg p-3 space-y-2">
          {/* Thread header */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              <Skeleton className="h-4 w-4 rounded mt-1" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-48" />
                <div className="flex items-center gap-2">
                  <Skeleton className="h-5 w-16 rounded-full" />
                  <Skeleton className="h-4 w-20" />
                </div>
                <div className="flex items-center gap-4">
                  <Skeleton className="h-3 w-12" />
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-3 w-8" />
                </div>
              </div>
            </div>
          </div>

          {/* Expanded messages (for some threads) */}
          {i === 0 && (
            <div className="mt-3 space-y-2">
              <div className="ml-6 p-2 rounded bg-primary/10">
                <Skeleton className="h-4 w-64 mb-1" />
                <Skeleton className="h-3 w-16" />
              </div>
              <div className="mr-6 p-2 rounded bg-secondary/10">
                <Skeleton className="h-4 w-72 mb-1" />
                <Skeleton className="h-4 w-48 mb-1" />
                <Skeleton className="h-3 w-16" />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

interface AgentBarSkeletonProps {
  className?: string;
}

export function AgentBarSkeleton({ className }: AgentBarSkeletonProps) {
  return (
    <div className={`flex items-center justify-between p-3 border-b border-border/30 ${className || ''}`}>
      <div className="flex items-center gap-4">
        {/* Agent status indicators */}
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton className="h-2 w-2 rounded-full" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-5 w-8 rounded" />
          </div>
        ))}
      </div>
      
      {/* Token and dollar counters */}
      <div className="flex items-center gap-4">
        <Skeleton className="h-4 w-12" />
        <Skeleton className="h-4 w-8" />
      </div>
    </div>
  );
}

interface CodeEditorSkeletonProps {
  className?: string;
}

export function CodeEditorSkeleton({ className }: CodeEditorSkeletonProps) {
  return (
    <div className={`h-full flex flex-col ${className || ''}`}>
      {/* Header with tabs */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex gap-2">
            <Skeleton className="h-8 w-24 rounded" />
            <Skeleton className="h-8 w-20 rounded" />
          </div>
          <div className="flex gap-1">
            <Skeleton className="h-8 w-8 rounded" />
            <Skeleton className="h-8 w-8 rounded" />
            <Skeleton className="h-8 w-8 rounded" />
          </div>
        </div>
      </div>

      {/* Agent bar skeleton */}
      <AgentBarSkeleton />

      {/* Code content */}
      <div className="flex-1 flex">
        {/* Gutter */}
        <div className="w-16 border-r border-border/30 p-2">
          <Skeleton className="h-32 w-2 rounded-full mx-auto" />
        </div>
        
        {/* Code lines */}
        <div className="flex-1 p-4 space-y-2">
          {[...Array(20)].map((_, i) => (
            <div key={i} className="flex gap-2">
              <Skeleton className="h-4 w-6" />
              <Skeleton className={`h-4 w-${Math.floor(Math.random() * 64) + 16}`} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}