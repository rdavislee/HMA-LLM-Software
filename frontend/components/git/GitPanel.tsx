import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  GitBranch, 
  GitCommit, 
  Plus, 
  Minus, 
  Upload, 
  Download,
  History,
  Play,
  Check,
  X,
  ChevronDown,
  ChevronRight,
  FileText,
  Clock,
  User,
  GitPullRequest,
  RefreshCw,
  AlertCircle,
  Loader2,
  Search,
  Filter,
  MoreVertical,
  Package,
  FolderGit,
  AlertTriangle,
  CheckSquare,
  Square,
  GitMerge
} from 'lucide-react';
import websocketService, { 
  GitStatus, 
  GitCommit as GitCommitType, 
  GitBranch as GitBranchType, 
  GitDiff,
  GitUpdate 
} from '../../src/services/websocket';

interface GitPanelProps {
  isOpen: boolean;
  onClose?: () => void;
}

interface CommitFormData {
  message: string;
  authorName: string;
  authorEmail: string;
}

interface OperationStatus {
  type: 'error' | 'success' | 'info';
  message: string;
}

interface ConfirmDialog {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
}

type GitTab = 'changes' | 'history' | 'branches' | 'stash';

const GitPanel: React.FC<GitPanelProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<GitTab>('changes');
  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null);
  const [commits, setCommits] = useState<GitCommitType[]>([]);
  const [branches, setBranches] = useState<GitBranchType[]>([]);
  const [selectedDiff, setSelectedDiff] = useState<GitDiff | null>(null);
  const [showCommitForm, setShowCommitForm] = useState(false);
  const [commitForm, setCommitForm] = useState<CommitFormData>({
    message: '',
    authorName: localStorage.getItem('git-author-name') || '',
    authorEmail: localStorage.getItem('git-author-email') || ''
  });
  const [expandedCommits, setExpandedCommits] = useState<Set<string>>(new Set());
  
  // New state for enhanced functionality
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});
  const [operationStatus, setOperationStatus] = useState<OperationStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'author' | 'message'>('all');
  const [confirmDialog, setConfirmDialog] = useState<ConfirmDialog>({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {}
  });
  const [showBranchMenu, setShowBranchMenu] = useState<string | null>(null);
  const [newBranchName, setNewBranchName] = useState('');
  const [showNewBranchForm, setShowNewBranchForm] = useState(false);
  const [projectLoaded, setProjectLoaded] = useState(false);

  // Check if a project is loaded
  useEffect(() => {
    const checkProjectStatus = () => {
      // Listen for project status updates
      websocketService.on('project_status', (data) => {
        if (data.status === 'active' || data.status === 'initializing') {
          setProjectLoaded(true);
        } else {
          setProjectLoaded(false);
          // Clear git data when project is cleared/error
          setGitStatus(null);
          setCommits([]);
          setBranches([]);
        }
      });

      // Check if there's already a project loaded (in case GitPanel was reopened)
      // This would require the server to send project status on reconnect or we maintain state in a parent component
      // For now, we'll assume the project state is maintained by the parent
    };

    checkProjectStatus();

    return () => {
      websocketService.off('project_status');
    };
  }, []);

  // Auto-hide operation status after 3 seconds
  useEffect(() => {
    if (operationStatus) {
      const timer = setTimeout(() => setOperationStatus(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [operationStatus]);

  const refreshGitData = useCallback(async () => {
    if (!projectLoaded) return;
    
    try {
      setIsLoading(prev => ({ ...prev, refresh: true }));
      websocketService.requestGitStatus();
      websocketService.requestGitCommits(50);
      websocketService.requestGitBranches();
    } catch (error) {
      console.error('Error refreshing git data:', error);
    } finally {
      setIsLoading(prev => ({ ...prev, refresh: false }));
    }
  }, [projectLoaded]);

  // Load git data when panel opens
  useEffect(() => {
    if (isOpen && projectLoaded) {
      refreshGitData();
    }
  }, [isOpen, projectLoaded, refreshGitData]);

  // Set up WebSocket event listeners
  useEffect(() => {
    websocketService.on('git_status', (data) => {
      setGitStatus(data.status);
    });

    websocketService.on('git_commits', (data) => {
      setCommits(data.commits);
    });

    websocketService.on('git_branches', (data) => {
      setBranches(data.branches);
    });

    websocketService.on('git_diff', (data) => {
      setSelectedDiff(data.diff);
    });

    websocketService.on('git_update', (update: GitUpdate) => {
      // Refresh data on git updates
      websocketService.requestGitStatus();
      if (update.eventType === 'head_changed') {
        websocketService.requestGitCommits();
        websocketService.requestGitBranches();
      }
    });

    websocketService.on('git_stage_result', (data) => {
      setIsLoading(prev => ({ ...prev, [`stage-${data.filePath}`]: false }));
      if (data.success) {
        setOperationStatus({ type: 'success', message: 'File staged successfully' });
        websocketService.requestGitStatus();
      } else {
        setOperationStatus({ type: 'error', message: 'Failed to stage file' });
      }
    });

    websocketService.on('git_unstage_result', (data) => {
      setIsLoading(prev => ({ ...prev, [`unstage-${data.filePath}`]: false }));
      if (data.success) {
        setOperationStatus({ type: 'success', message: 'File unstaged successfully' });
        websocketService.requestGitStatus();
      } else {
        setOperationStatus({ type: 'error', message: 'Failed to unstage file' });
      }
    });

    websocketService.on('git_commit_result', (data) => {
      setIsLoading(prev => ({ ...prev, commit: false }));
      if (data.success) {
        setOperationStatus({ type: 'success', message: 'Changes committed successfully' });
        setShowCommitForm(false);
        setCommitForm(prev => ({ ...prev, message: '' }));
        websocketService.requestGitStatus();
        websocketService.requestGitCommits();
      } else {
        setOperationStatus({ type: 'error', message: data.error || 'Failed to commit changes' });
      }
    });

    websocketService.on('git_checkout_result', (data) => {
      setIsLoading(prev => ({ ...prev, checkout: false }));
      if (data.success) {
        setOperationStatus({ type: 'success', message: `Switched to branch ${data.branchName}` });
        websocketService.requestGitStatus();
        websocketService.requestGitBranches();
      } else {
        setOperationStatus({ type: 'error', message: 'Failed to switch branch' });
      }
    });

    websocketService.on('git_push_result', (data) => {
      setIsLoading(prev => ({ ...prev, push: false }));
      if (data.success) {
        setOperationStatus({ type: 'success', message: 'Changes pushed successfully' });
        websocketService.requestGitStatus();
      } else {
        setOperationStatus({ type: 'error', message: 'Failed to push changes' });
      }
    });

    websocketService.on('git_pull_result', (data) => {
      setIsLoading(prev => ({ ...prev, pull: false }));
      if (data.success) {
        setOperationStatus({ type: 'success', message: 'Changes pulled successfully' });
        websocketService.requestGitStatus();
        websocketService.requestGitCommits();
      } else {
        setOperationStatus({ type: 'error', message: 'Failed to pull changes' });
      }
    });

    return () => {
      websocketService.off('git_status');
      websocketService.off('git_commits');
      websocketService.off('git_branches');
      websocketService.off('git_diff');
      websocketService.off('git_update');
      websocketService.off('git_stage_result');
      websocketService.off('git_unstage_result');
      websocketService.off('git_commit_result');
      websocketService.off('git_checkout_result');
      websocketService.off('git_push_result');
      websocketService.off('git_pull_result');
    };
  }, []);

  const handleStageFile = (filePath: string) => {
    if (!projectLoaded) return;
    setIsLoading(prev => ({ ...prev, [`stage-${filePath}`]: true }));
    websocketService.stageFile(filePath);
  };

  const handleUnstageFile = (filePath: string) => {
    if (!projectLoaded) return;
    setIsLoading(prev => ({ ...prev, [`unstage-${filePath}`]: true }));
    websocketService.unstageFile(filePath);
  };

  const handleStageAll = () => {
    if (!gitStatus || !projectLoaded) return;
    const allUnstaged = [...gitStatus.unstaged_files, ...gitStatus.untracked_files];
    allUnstaged.forEach(file => handleStageFile(file.file_path));
  };

  const handleUnstageAll = () => {
    if (!gitStatus || !projectLoaded) return;
    gitStatus.staged_files.forEach(file => handleUnstageFile(file.file_path));
  };

  const handleViewDiff = (filePath: string, staged: boolean = false) => {
    if (!projectLoaded) return;
    websocketService.requestGitDiff(filePath, staged);
  };

  const handleCommit = () => {
    if (!commitForm.message.trim() || !projectLoaded) return;
    
    setIsLoading(prev => ({ ...prev, commit: true }));
    
    // Save author info to localStorage
    localStorage.setItem('git-author-name', commitForm.authorName);
    localStorage.setItem('git-author-email', commitForm.authorEmail);
    
    websocketService.commitChanges(
      commitForm.message,
      commitForm.authorName || undefined,
      commitForm.authorEmail || undefined
    );
  };

  const handleCheckoutBranch = (branchName: string) => {
    if (!projectLoaded) return;
    setConfirmDialog({
      isOpen: true,
      title: 'Switch Branch',
      message: `Are you sure you want to switch to branch "${branchName}"? Any uncommitted changes will be lost.`,
      onConfirm: () => {
        setIsLoading(prev => ({ ...prev, checkout: true }));
        websocketService.checkoutBranch(branchName);
        setConfirmDialog({ ...confirmDialog, isOpen: false });
      }
    });
  };

  const handlePush = () => {
    if (!projectLoaded) return;
    setIsLoading(prev => ({ ...prev, push: true }));
    websocketService.pushChanges();
  };

  const handlePull = () => {
    if (!projectLoaded) return;
    setIsLoading(prev => ({ ...prev, pull: true }));
    websocketService.pullChanges();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'M': return <span className="text-blue-400 font-bold">M</span>;
      case 'A': return <span className="text-green-400 font-bold">A</span>;
      case 'D': return <span className="text-red-400 font-bold">D</span>;
      case 'R': return <span className="text-purple-400 font-bold">R</span>;
      case '??': return <span className="text-gray-400 font-bold">?</span>;
      default: return <span className="text-gray-400 font-bold">{status}</span>;
    }
  };

  const getStatusDescription = (status: string) => {
    switch (status) {
      case 'M': return 'Modified';
      case 'A': return 'Added';
      case 'D': return 'Deleted';
      case 'R': return 'Renamed';
      case '??': return 'Untracked';
      default: return status;
    }
  };

  const toggleCommitExpansion = (commitHash: string) => {
    setExpandedCommits(prev => {
      const newSet = new Set(prev);
      if (newSet.has(commitHash)) {
        newSet.delete(commitHash);
      } else {
        newSet.add(commitHash);
      }
      return newSet;
    });
  };

  const formatCommitTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 30) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  // Filter commits based on search query
  const filteredCommits = useMemo(() => {
    if (!searchQuery) return commits;
    
    const query = searchQuery.toLowerCase();
    return commits.filter(commit => {
      switch (filterType) {
        case 'author':
          return commit.author_name.toLowerCase().includes(query) ||
                 commit.author_email.toLowerCase().includes(query);
        case 'message':
          return commit.message.toLowerCase().includes(query);
        default:
          return commit.message.toLowerCase().includes(query) ||
                 commit.author_name.toLowerCase().includes(query) ||
                 commit.author_email.toLowerCase().includes(query);
      }
    });
  }, [commits, searchQuery, filterType]);

  const formatDiffContent = (content: string) => {
    return content.split('\n').map((line, index) => {
      let className = 'text-gray-300';
      if (line.startsWith('+') && !line.startsWith('+++')) {
        className = 'text-green-400 bg-green-900/20';
      } else if (line.startsWith('-') && !line.startsWith('---')) {
        className = 'text-red-400 bg-red-900/20';
      } else if (line.startsWith('@@')) {
        className = 'text-blue-400 bg-blue-900/20';
      } else if (line.startsWith('diff') || line.startsWith('index')) {
        className = 'text-yellow-400';
      }
      
      return (
        <div key={index} className={`${className} px-2`}>
          {line || ' '}
        </div>
      );
    });
  };

  if (!isOpen) return null;

  return (
    <div className="w-80 h-full bg-gray-900 border-l border-yellow-400/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-yellow-400" />
            <h2 className="text-yellow-400 font-semibold text-lg">Git</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={refreshGitData}
              disabled={isLoading.refresh}
              className="p-1 rounded hover:bg-gray-700 transition-colors disabled:opacity-50"
              title="Refresh"
            >
              {isLoading.refresh ? (
                <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 text-gray-400" />
              )}
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="p-1 rounded hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            )}
          </div>
        </div>
        
        {gitStatus && (
          <div className="mt-2 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <FolderGit className="w-4 h-4" />
              <span className="font-medium">{gitStatus.current_branch}</span>
              {gitStatus.ahead > 0 && (
                <span className="text-green-400 flex items-center gap-1">
                  <Upload className="w-3 h-3" />
                  {gitStatus.ahead}
                </span>
              )}
              {gitStatus.behind > 0 && (
                <span className="text-red-400 flex items-center gap-1">
                  <Download className="w-3 h-3" />
                  {gitStatus.behind}
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Operation Status */}
      {operationStatus && (
        <div className={`px-4 py-2 text-sm flex items-center gap-2 ${
          operationStatus.type === 'error' ? 'bg-red-900/20 text-red-400' :
          operationStatus.type === 'success' ? 'bg-green-900/20 text-green-400' :
          'bg-blue-900/20 text-blue-400'
        }`}>
          {operationStatus.type === 'error' ? (
            <AlertCircle className="w-4 h-4" />
          ) : (
            <Check className="w-4 h-4" />
          )}
          <span>{operationStatus.message}</span>
        </div>
      )}

      {/* No Project Loaded State */}
      {!projectLoaded ? (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <FolderGit className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-400 mb-2">No Project Loaded</h3>
            <p className="text-sm text-gray-500 max-w-xs">
              Import a project to start using Git features. You can track changes, commit code, and manage branches.
            </p>
          </div>
        </div>
      ) : (
        <>
          {/* Tabs */}
          <div className="flex border-b border-yellow-400/20">
            {[
              { id: 'changes', label: 'Changes', icon: FileText },
              { id: 'history', label: 'History', icon: History },
              { id: 'branches', label: 'Branches', icon: GitBranch },
              { id: 'stash', label: 'Stash', icon: Package }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as GitTab)}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm transition-colors ${
                  activeTab === id
                    ? 'text-yellow-400 border-b-2 border-yellow-400'
                    : 'text-gray-400 hover:text-yellow-400'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'changes' && (
              <div className="p-4 space-y-4">
                {/* Stage/Unstage All Buttons */}
                {gitStatus && (gitStatus.unstaged_files.length > 0 || gitStatus.untracked_files.length > 0) && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleStageAll}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white text-sm rounded transition-colors"
                    >
                      <CheckSquare className="w-4 h-4" />
                      <span>Stage All</span>
                    </button>
                    {gitStatus.staged_files.length > 0 && (
                      <button
                        onClick={handleUnstageAll}
                        className="flex-1 flex items-center justify-center gap-2 px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-sm rounded transition-colors"
                      >
                        <Square className="w-4 h-4" />
                        <span>Unstage All</span>
                      </button>
                    )}
                  </div>
                )}

                {/* Staged Files */}
                {gitStatus?.staged_files && gitStatus.staged_files.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                      <span>Staged Changes</span>
                      <span className="text-xs bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded">
                        {gitStatus.staged_files.length}
                      </span>
                    </h3>
                    <div className="space-y-1">
                      {gitStatus.staged_files.map((file) => (
                        <div key={file.file_path} className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded group">
                          <div className="flex items-center gap-1" title={getStatusDescription(file.status)}>
                            {getStatusIcon(file.status)}
                          </div>
                          <span className="flex-1 text-sm text-gray-300 font-mono truncate" title={file.file_path}>
                            {file.file_path}
                          </span>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleViewDiff(file.file_path, true)}
                              className="p-1 hover:bg-gray-700 rounded"
                              title="View diff"
                            >
                              <FileText className="w-3 h-3 text-gray-400" />
                            </button>
                            <button
                              onClick={() => handleUnstageFile(file.file_path)}
                              disabled={isLoading[`unstage-${file.file_path}`]}
                              className="p-1 hover:bg-gray-700 rounded disabled:opacity-50"
                              title="Unstage"
                            >
                              {isLoading[`unstage-${file.file_path}`] ? (
                                <Loader2 className="w-3 h-3 text-gray-400 animate-spin" />
                              ) : (
                                <Minus className="w-3 h-3 text-red-400" />
                              )}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Unstaged Files */}
                {gitStatus?.unstaged_files && gitStatus.unstaged_files.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                      <span>Changes</span>
                      <span className="text-xs bg-yellow-500/20 text-yellow-400 px-1.5 py-0.5 rounded">
                        {gitStatus.unstaged_files.length}
                      </span>
                    </h3>
                    <div className="space-y-1">
                      {gitStatus.unstaged_files.map((file) => (
                        <div key={file.file_path} className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded group">
                          <div className="flex items-center gap-1" title={getStatusDescription(file.status)}>
                            {getStatusIcon(file.status)}
                          </div>
                          <span className="flex-1 text-sm text-gray-300 font-mono truncate" title={file.file_path}>
                            {file.file_path}
                          </span>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleViewDiff(file.file_path, false)}
                              className="p-1 hover:bg-gray-700 rounded"
                              title="View diff"
                            >
                              <FileText className="w-3 h-3 text-gray-400" />
                            </button>
                            <button
                              onClick={() => handleStageFile(file.file_path)}
                              disabled={isLoading[`stage-${file.file_path}`]}
                              className="p-1 hover:bg-gray-700 rounded disabled:opacity-50"
                              title="Stage"
                            >
                              {isLoading[`stage-${file.file_path}`] ? (
                                <Loader2 className="w-3 h-3 text-gray-400 animate-spin" />
                              ) : (
                                <Plus className="w-3 h-3 text-green-400" />
                              )}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Untracked Files */}
                {gitStatus?.untracked_files && gitStatus.untracked_files.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                      <span>Untracked Files</span>
                      <span className="text-xs bg-gray-500/20 text-gray-400 px-1.5 py-0.5 rounded">
                        {gitStatus.untracked_files.length}
                      </span>
                    </h3>
                    <div className="space-y-1">
                      {gitStatus.untracked_files.map((file) => (
                        <div key={file.file_path} className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded group">
                          <div className="flex items-center gap-1" title={getStatusDescription(file.status)}>
                            {getStatusIcon(file.status)}
                          </div>
                          <span className="flex-1 text-sm text-gray-300 font-mono truncate" title={file.file_path}>
                            {file.file_path}
                          </span>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleStageFile(file.file_path)}
                              disabled={isLoading[`stage-${file.file_path}`]}
                              className="p-1 hover:bg-gray-700 rounded disabled:opacity-50"
                              title="Stage"
                            >
                              {isLoading[`stage-${file.file_path}`] ? (
                                <Loader2 className="w-3 h-3 text-gray-400 animate-spin" />
                              ) : (
                                <Plus className="w-3 h-3 text-green-400" />
                              )}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Commit Section */}
                {gitStatus?.staged_files && gitStatus.staged_files.length > 0 && (
                  <div className="border-t border-gray-700 pt-4">
                    {!showCommitForm ? (
                      <button
                        onClick={() => setShowCommitForm(true)}
                        className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded transition-colors"
                      >
                        <GitCommit className="w-4 h-4" />
                        <span>Commit Changes</span>
                      </button>
                    ) : (
                      <div className="space-y-3">
                        <textarea
                          value={commitForm.message}
                          onChange={(e) => setCommitForm(prev => ({ ...prev, message: e.target.value }))}
                          placeholder="Commit message..."
                          className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
                          rows={3}
                        />
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="text"
                            value={commitForm.authorName}
                            onChange={(e) => setCommitForm(prev => ({ ...prev, authorName: e.target.value }))}
                            placeholder="Author name"
                            className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
                          />
                          <input
                            type="email"
                            value={commitForm.authorEmail}
                            onChange={(e) => setCommitForm(prev => ({ ...prev, authorEmail: e.target.value }))}
                            placeholder="Author email"
                            className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={handleCommit}
                            disabled={!commitForm.message.trim() || isLoading.commit}
                            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-500 hover:bg-green-400 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
                          >
                            {isLoading.commit ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Check className="w-4 h-4" />
                            )}
                            <span>Commit</span>
                          </button>
                          <button
                            onClick={() => setShowCommitForm(false)}
                            className="px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Remote Actions */}
                {gitStatus && !gitStatus.is_detached && (
                  <div className="border-t border-gray-700 pt-4 space-y-2">
                    <button
                      onClick={handlePull}
                      disabled={isLoading.pull}
                      className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-500 hover:bg-blue-400 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
                    >
                      {isLoading.pull ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Download className="w-4 h-4" />
                      )}
                      <span>Pull</span>
                    </button>
                    <button
                      onClick={handlePush}
                      disabled={isLoading.push}
                      className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-purple-500 hover:bg-purple-400 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
                    >
                      {isLoading.push ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Upload className="w-4 h-4" />
                      )}
                      <span>Push</span>
                    </button>
                  </div>
                )}

                {/* No changes message */}
                {gitStatus && !gitStatus.is_dirty && (
                  <div className="text-center py-8 text-gray-500">
                    <GitBranch className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No changes</p>
                    <p className="text-sm">Working tree clean</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'history' && (
              <div className="p-4">
                {/* Search and Filter */}
                <div className="mb-4 space-y-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search commits..."
                      className="w-full pl-10 pr-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-gray-400" />
                    <select
                      value={filterType}
                      onChange={(e) => setFilterType(e.target.value as 'all' | 'author' | 'message')}
                      className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 focus:outline-none focus:border-yellow-400"
                    >
                      <option value="all">All fields</option>
                      <option value="author">Author only</option>
                      <option value="message">Message only</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-3">
                  {filteredCommits.map((commit) => {
                    const isExpanded = expandedCommits.has(commit.hash);
                    return (
                      <div key={commit.hash} className="border border-gray-700 rounded p-3 hover:border-gray-600 transition-colors">
                        <div 
                          className="flex items-start gap-3 cursor-pointer"
                          onClick={() => toggleCommitExpansion(commit.hash)}
                        >
                          <button className="p-0.5 mt-0.5">
                            {isExpanded ? (
                              <ChevronDown className="w-3 h-3 text-gray-400" />
                            ) : (
                              <ChevronRight className="w-3 h-3 text-gray-400" />
                            )}
                          </button>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-100 font-medium truncate">
                              {commit.message}
                            </p>
                            <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
                              <User className="w-3 h-3" />
                              <span>{commit.author_name}</span>
                              <Clock className="w-3 h-3 ml-2" />
                              <span>{formatCommitTime(commit.timestamp)}</span>
                            </div>
                          </div>
                          <span className="text-xs text-yellow-400 font-mono">
                            {commit.short_hash}
                          </span>
                        </div>
                        
                        {isExpanded && (
                          <div className="mt-3 pt-3 border-t border-gray-700">
                            <div className="text-xs text-gray-400 space-y-1">
                              <p><strong>Author:</strong> {commit.author_email}</p>
                              <p><strong>Commit:</strong> {commit.hash}</p>
                              {commit.parents.length > 0 && (
                                <p><strong>Parents:</strong> {commit.parents.join(', ')}</p>
                              )}
                              {commit.files_changed.length > 0 && (
                                <div>
                                  <strong>Files changed ({commit.files_changed.length}):</strong>
                                  <div className="mt-1 max-h-20 overflow-y-auto">
                                    {commit.files_changed.map((file, idx) => (
                                      <div key={idx} className="font-mono text-xs text-gray-300 hover:text-yellow-400 cursor-pointer">
                                        {file}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  
                  {filteredCommits.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>{searchQuery ? 'No commits found matching your search' : 'No commits found'}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'branches' && (
              <div className="p-4">
                {/* New Branch Button */}
                <button
                  onClick={() => setShowNewBranchForm(!showNewBranchForm)}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded transition-colors mb-4"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Branch</span>
                </button>

                {/* New Branch Form */}
                {showNewBranchForm && (
                  <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
                    <input
                      type="text"
                      value={newBranchName}
                      onChange={(e) => setNewBranchName(e.target.value)}
                      placeholder="Branch name..."
                      className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400 mb-2"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          // TODO: Implement branch creation
                          setOperationStatus({ type: 'info', message: 'Branch creation not implemented yet' });
                          setShowNewBranchForm(false);
                          setNewBranchName('');
                        }}
                        disabled={!newBranchName.trim()}
                        className="flex-1 px-3 py-1 bg-green-500 hover:bg-green-400 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
                      >
                        Create
                      </button>
                      <button
                        onClick={() => {
                          setShowNewBranchForm(false);
                          setNewBranchName('');
                        }}
                        className="px-3 py-1 bg-gray-600 hover:bg-gray-500 text-white rounded text-sm transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  {branches.filter(b => !b.is_remote).map((branch) => (
                    <div 
                      key={branch.name}
                      className={`flex items-center gap-3 p-3 rounded border transition-colors ${
                        branch.is_current 
                          ? 'border-yellow-400 bg-yellow-400/10' 
                          : 'border-gray-700 hover:border-gray-600 hover:bg-gray-800'
                      }`}
                    >
                      <GitBranch className={`w-4 h-4 ${branch.is_current ? 'text-yellow-400' : 'text-gray-400'}`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-sm font-medium ${branch.is_current ? 'text-yellow-400' : 'text-gray-300'}`}>
                            {branch.name}
                          </span>
                          {branch.is_current && (
                            <span className="text-xs bg-yellow-400/20 text-yellow-400 px-1.5 py-0.5 rounded">
                              current
                            </span>
                          )}
                        </div>
                        {branch.last_commit_message && (
                          <p className="text-xs text-gray-400 truncate mt-1">
                            {branch.last_commit_message}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-1">
                        {!branch.is_current && (
                          <>
                            <button
                              onClick={() => handleCheckoutBranch(branch.name)}
                              className="p-1 hover:bg-gray-700 rounded"
                              title="Checkout branch"
                            >
                              <Play className="w-3 h-3 text-gray-400" />
                            </button>
                            <button
                              onClick={() => setShowBranchMenu(showBranchMenu === branch.name ? null : branch.name)}
                              className="p-1 hover:bg-gray-700 rounded relative"
                              title="More options"
                            >
                              <MoreVertical className="w-3 h-3 text-gray-400" />
                            </button>
                          </>
                        )}
                      </div>
                      
                      {/* Branch Menu */}
                      {showBranchMenu === branch.name && (
                        <div className="absolute right-4 mt-8 bg-gray-800 border border-gray-700 rounded shadow-lg z-10">
                          <button
                            onClick={() => {
                              setOperationStatus({ type: 'info', message: 'Merge not implemented yet' });
                              setShowBranchMenu(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                          >
                            <GitMerge className="w-4 h-4" />
                            Merge into current
                          </button>
                          <button
                            onClick={() => {
                              setOperationStatus({ type: 'info', message: 'Delete not implemented yet' });
                              setShowBranchMenu(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-700 flex items-center gap-2"
                          >
                            <X className="w-4 h-4" />
                            Delete branch
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {branches.filter(b => !b.is_remote).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <GitBranch className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No local branches found</p>
                    </div>
                  )}
                </div>
                
                {/* Remote branches section */}
                {branches.filter(b => b.is_remote).length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                      <GitPullRequest className="w-4 h-4" />
                      Remote Branches
                    </h3>
                    <div className="space-y-1">
                      {branches.filter(b => b.is_remote).map((branch) => (
                        <div key={branch.name} className="flex items-center gap-3 p-2 text-sm text-gray-400">
                          <GitBranch className="w-3 h-3" />
                          <span className="font-mono">{branch.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'stash' && (
              <div className="p-4">
                <div className="text-center py-8 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Stash functionality coming soon</p>
                  <p className="text-sm mt-2">Save your work in progress for later</p>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Confirmation Dialog */}
      {confirmDialog.isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-yellow-400/20 rounded-lg p-6 max-w-md">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-yellow-400" />
              <h3 className="text-lg font-medium text-yellow-400">{confirmDialog.title}</h3>
            </div>
            <p className="text-gray-300 mb-6">{confirmDialog.message}</p>
            <div className="flex gap-3">
              <button
                onClick={confirmDialog.onConfirm}
                className="flex-1 px-4 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded transition-colors"
              >
                Confirm
              </button>
              <button
                onClick={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
                className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Diff Viewer Modal */}
      {selectedDiff && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-yellow-400/20 rounded-lg w-full max-w-4xl max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-yellow-400/20">
              <h3 className="text-yellow-400 font-medium flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {selectedDiff.file_path}
              </h3>
              <button
                onClick={() => setSelectedDiff(null)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>
            <div className="flex-1 overflow-auto bg-gray-950">
              <div className="font-mono text-xs">
                {selectedDiff.is_binary ? (
                  <div className="p-4 text-center text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>Binary file</p>
                    <p className="text-sm">Cannot display diff for binary files</p>
                  </div>
                ) : selectedDiff.diff_content ? (
                  formatDiffContent(selectedDiff.diff_content)
                ) : (
                  <div className="p-4 text-center text-gray-500">
                    <p>No changes to display</p>
                  </div>
                )}
              </div>
            </div>
            <div className="p-4 border-t border-yellow-400/20 text-sm text-gray-400">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <span className="text-green-400">+{selectedDiff.added_lines}</span>
                    <span>additions</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-red-400">-{selectedDiff.removed_lines}</span>
                    <span>deletions</span>
                  </span>
                </div>
                <button
                  onClick={() => setSelectedDiff(null)}
                  className="px-4 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitPanel; 