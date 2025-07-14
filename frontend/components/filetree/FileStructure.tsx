import React, { useState, useMemo } from 'react';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen, Code, FileText, Image, Loader2 } from 'lucide-react';
import { AgentUpdate } from '../../src/services/websocket';
import { FileNode, ImportedFile } from '../../src/types';
import { useSocketEvent } from '../../src/hooks/useSocketEvent';

interface FileTreeProps {
  onFileSelect?: (filePath: string, content?: string) => void;
  importedFiles?: ImportedFile[];
  projectFiles?: FileNode[];
}

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

const FileTree: React.FC<FileTreeProps> = ({ onFileSelect, importedFiles = [], projectFiles = [] }) => {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [activeAgents, setActiveAgents] = useState<Map<string, AgentUpdate>>(new Map());

  const activeAgentPaths = useMemo(() => {
    const paths = new Set<string>();
    for (const [agentId, agent] of activeAgents) {
      if (agent.status === 'active') {
        // This is still a guess. A better implementation would have a defined way
        // to get a file path from an agent update.
        paths.add(agentId); 
      }
    }
    return paths;
  }, [activeAgents]);

  // Use the useSocketEvent hook instead of manual listener management
  useSocketEvent('agent_update', (update: AgentUpdate) => {
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

  const isAgentActive = (path: string): boolean => {
    // Check if any agent is working on this file or directory
    for (const agentPath of activeAgentPaths) {
      if (agentPath.includes(path) || path.includes(agentPath)) {
        return true;
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
            isSelected ? 'bg-gray-800 border-l-2 border-amber-400' : ''
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
              <FolderOpen className="w-4 h-4 text-amber-400" />
            ) : (
              <Folder className="w-4 h-4 text-amber-400" />
            )
          ) : (
            getFileIcon(node.name)
          )}
          
          <span className={`text-sm flex-1 ${isSelected ? 'text-amber-400' : 'text-gray-500'}`}>
            {node.name}
          </span>
          
          {isActive && (
            <Loader2 className="w-3 h-3 animate-spin text-amber-400" />
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
    <div className="h-full flex flex-col">
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
    </div>
  );
};

export default FileTree;
