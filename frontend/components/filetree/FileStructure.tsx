import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen, Code, FileText, Image, Loader2 } from 'lucide-react';
import websocketService, { AgentUpdate } from '../../src/services/websocket';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  content?: string;
  children?: FileNode[];
}

interface ImportedFile {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  content?: string;
}

interface FileTreeProps {
  onFileSelect?: (filePath: string, content?: string) => void;
  importedFiles?: ImportedFile[];
  projectFiles?: FileNode[];
}

const FileTree: React.FC<FileTreeProps> = ({ onFileSelect, importedFiles = [], projectFiles = [] }) => {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [activeAgents, setActiveAgents] = useState<Map<string, AgentUpdate>>(new Map());

  // Listen for agent updates
  useEffect(() => {
    websocketService.on('agent_update', (update: AgentUpdate) => {
      setActiveAgents(prev => {
        const newMap = new Map(prev);
        if (update.status === 'inactive' || update.status === 'completed') {
          newMap.delete(update.agentId);
        } else {
          newMap.set(update.agentId, update);
        }
        return newMap;
      });
    });

    return () => {
      websocketService.off('agent_update');
    };
  }, []);

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const handleFileClick = (node: FileNode) => {
    if (node.type === 'file') {
      setSelectedFile(node.path);
      onFileSelect?.(node.path, node.content);
    } else {
      toggleFolder(node.path);
    }
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        return <Code className="w-4 h-4 text-yellow-400" />;
      case 'json':
      case 'md':
      case 'txt':
        return <FileText className="w-4 h-4 text-blue-400" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'svg':
        return <Image className="w-4 h-4 text-green-400" />;
      case 'css':
      case 'scss':
      case 'sass':
        return <FileText className="w-4 h-4 text-pink-400" />;
      case 'html':
        return <FileText className="w-4 h-4 text-orange-400" />;
      default:
        return <File className="w-4 h-4 text-gray-400" />;
    }
  };

  const isAgentActive = (path: string): boolean => {
    // Check if any agent is working on this file or directory
    for (const [agentId, agent] of activeAgents) {
      if (agentId.includes(path) || path.includes(agentId)) {
        return agent.status === 'active';
      }
    }
    return false;
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;
    const isActive = isAgentActive(node.path);

    return (
      <div key={node.path}>
        <div
          className={`flex items-center gap-2 px-2 py-1 hover:bg-gray-800 cursor-pointer transition-colors ${
            isSelected ? 'bg-gray-800 border-l-2 border-yellow-400' : ''
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => handleFileClick(node)}
        >
          {node.type === 'directory' && (
            <span className="text-gray-400">
              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </span>
          )}
          
          {node.type === 'directory' ? (
            isExpanded ? (
              <FolderOpen className="w-4 h-4 text-yellow-400" />
            ) : (
              <Folder className="w-4 h-4 text-yellow-400" />
            )
          ) : (
            getFileIcon(node.name)
          )}
          
          <span className={`text-sm flex-1 ${isSelected ? 'text-yellow-400' : 'text-gray-300'}`}>
            {node.name}
          </span>
          
          {isActive && (
            <Loader2 className="w-3 h-3 animate-spin text-yellow-400" />
          )}
        </div>
        
        {node.type === 'directory' && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  // Convert imported files to FileNode structure if needed
  const convertImportedFiles = (files: ImportedFile[]): FileNode[] => {
    const root: FileNode[] = [];
    
    files.forEach(file => {
      const parts = file.path.split('/');
      let current = root;
      
      parts.forEach((part, index) => {
        const isLast = index === parts.length - 1;
        const path = parts.slice(0, index + 1).join('/');
        
        let node = current.find(n => n.name === part);
        if (!node) {
          node = {
            name: part,
            path: path,
            type: isLast && file.type === 'file' ? 'file' : 'directory',
            content: isLast ? file.content : undefined,
            children: isLast && file.type === 'file' ? undefined : []
          };
          current.push(node);
        }
        
        if (node.children) {
          current = node.children;
        }
      });
    });
    
    return root;
  };

  // Use project files if available, otherwise fall back to imported files
  const filesToDisplay = projectFiles.length > 0 ? projectFiles : convertImportedFiles(importedFiles);

  return (
    <div className="h-full bg-gray-900 border-r border-yellow-400/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-yellow-400 font-semibold text-lg">Project Files</h2>
        </div>
        {activeAgents.size > 0 && (
          <p className="text-xs text-gray-400 mt-1">
            {activeAgents.size} agent{activeAgents.size > 1 ? 's' : ''} working
          </p>
        )}
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto p-2">
        {filesToDisplay.length === 0 ? (
          <div className="text-center text-gray-500 text-sm mt-8">
            <Folder className="w-12 h-12 mx-auto mb-2 opacity-20" />
            <p>No files yet</p>
            <p className="text-xs mt-1">Start a conversation to generate code</p>
          </div>
        ) : (
          filesToDisplay.map(node => renderNode(node))
        )}
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-yellow-400/20 text-xs text-gray-400">
        <div className="flex items-center justify-between">
          <span>{filesToDisplay.length} items</span>
          <span className="text-yellow-400">
            {activeAgents.size > 0 ? 'Building...' : 'Ready'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default FileTree;
