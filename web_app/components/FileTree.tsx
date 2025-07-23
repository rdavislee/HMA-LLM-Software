import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { 
  ChevronRight, 
  ChevronDown,
  Plus,
  File,
  FileText,
  Image,
  Code,
  Database,
  Folder,
  FolderOpen,
  Download
} from 'lucide-react';
import websocketService, { FileTreeUpdate } from '../services/websocket';
import { useSocketEvent } from '../hooks/useSocketEvent';
import { ImportedNode, FileImportService } from '../services/fileImport';

interface FileNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  isExpanded?: boolean;
  content?: string;
  language?: string;
}

interface FileTreeProps {
  onFileSelect?: (path: string, content?: string, language?: string) => void;
  importedProject?: ImportedNode[];
}

export function FileTree({ onFileSelect, importedProject = [] }: FileTreeProps) {
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  // Update file tree when imported project changes
  useEffect(() => {
    if (importedProject.length > 0) {
      const convertedNodes = FileImportService.convertToFileTreeNodes(importedProject);
      setFileTree(convertedNodes);
    }
  }, [importedProject]);

  // Handle file tree updates from WebSocket
  useSocketEvent('file_tree_update', (update: FileTreeUpdate) => {
    setFileTree(prevTree => {
      const newTree = [...prevTree];
      
      const pathParts = update.filePath.split('/');
      
      // Helper function to find or create path in tree
      const updateTreeNode = (nodes: FileNode[], parts: string[], depth: number = 0): FileNode[] => {
        if (depth === parts.length - 1) {
          // We're at the file/folder to update
          const existingIndex = nodes.findIndex(n => n.name === parts[depth]);
          
          if (update.action === 'delete') {
            return nodes.filter(n => n.name !== parts[depth]);
          } else if (update.action === 'create' || update.action === 'update') {
            const newNode: FileNode = {
              id: update.filePath,
              name: parts[depth] || 'unknown',
              path: update.filePath,
              type: update.fileType,
              children: update.fileType === 'folder' ? [] : undefined
            };
            
            if (existingIndex >= 0) {
              nodes[existingIndex] = { ...nodes[existingIndex], ...newNode };
            } else {
              nodes.push(newNode);
            }
          }
          return nodes;
        }
        
        // Navigate deeper into the tree
        const folderName = parts[depth] || 'unknown';
        let folder = nodes.find(n => n.name === folderName && n.type === 'folder');
        
        if (!folder) {
          // Create folder if it doesn't exist
          folder = {
            id: parts.slice(0, depth + 1).join('/'),
            name: folderName,
            path: parts.slice(0, depth + 1).join('/'),
            type: 'folder',
            children: [],
            isExpanded: false
          };
          nodes.push(folder);
        }
        
        if (folder?.children) {
          folder.children = updateTreeNode(folder.children, parts, depth + 1);
        }
        
        return nodes;
      };
      
      return updateTreeNode(newTree, pathParts);
    });
  });

  const toggleFolder = (nodeId: string) => {
    const updateNode = (nodes: FileNode[]): FileNode[] => {
      return nodes.map(node => {
        if (node.id === nodeId) {
          return { ...node, isExpanded: !node.isExpanded };
        }
        if (node.children) {
          return { ...node, children: updateNode(node.children) };
        }
        return node;
      });
    };
    setFileTree(updateNode(fileTree));
  };

  const handleFileSelect = (node: FileNode) => {
    if (node.type === 'file') {
      setSelectedFile(node.id);
      if (node.content) {
        // For imported files, we have the content available
        onFileSelect?.(node.path, node.content, node.language);
      } else {
        // For WebSocket files, request content from server
        websocketService.selectFile(node.path);
        onFileSelect?.(node.path);
      }
    }
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'tsx':
      case 'jsx':
      case 'ts':
      case 'js':
        return <Code className="h-3 w-3 text-blue-400" />;
      case 'json':
        return <Database className="h-3 w-3 text-yellow-400" />;
      case 'md':
        return <FileText className="h-3 w-3 text-gray-400" />;
      case 'html':
        return <Code className="h-3 w-3 text-orange-400" />;
      case 'css':
        return <Code className="h-3 w-3 text-purple-400" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'svg':
        return <Image className="h-3 w-3 text-green-400" />;
      default:
        return <File className="h-3 w-3 text-gray-400" />;
    }
  };

  const downloadProject = () => {
    // Create a zip-like structure for the project
    const projectData = {
      name: 'project-export',
      timestamp: new Date().toISOString(),
      files: [] as Array<{ path: string; content: string; language?: string }>
    };

    // Recursive function to extract all files
    const extractFiles = (nodes: FileNode[]) => {
      nodes.forEach(node => {
        if (node.type === 'file' && node.content) {
          projectData.files.push({
            path: node.path,
            content: node.content,
            language: node.language
          });
        } else if (node.type === 'folder' && node.children) {
          extractFiles(node.children);
        }
      });
    };

    extractFiles(fileTree);

    // Convert to JSON and download
    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `project-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearFileTree = () => {
    // Clear all contents from the file tree
    setFileTree([]);
    setSelectedFile(null);
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isSelected = selectedFile === node.id;
    
    return (
      <div key={node.id} className="file-tree-item">
        <div
          className={`flex items-center gap-1 px-2 py-1 cursor-pointer hover:bg-muted/20 file-tree-small ${
            isSelected ? 'bg-primary/10 text-primary' : 'text-foreground'
          }`}
          style={{ 
            paddingLeft: `${8 + depth * 12}px`,
            fontFamily: 'Quicksand, sans-serif'
          }}
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(node.id);
            } else {
              handleFileSelect(node);
            }
          }}
        >
          {node.type === 'folder' && (
            <>
              {node.isExpanded ? (
                <ChevronDown className="h-3 w-3 text-muted-foreground flex-shrink-0" />
              ) : (
                <ChevronRight className="h-3 w-3 text-muted-foreground flex-shrink-0" />
              )}
              <div className="w-3 flex justify-center">
                {node.isExpanded ? (
                  <FolderOpen className="h-3 w-3 text-primary" />
                ) : (
                  <Folder className="h-3 w-3 text-muted-foreground" />
                )}
              </div>
            </>
          )}
          
          {node.type === 'file' && (
            <div className="w-3 flex justify-center ml-3">
              {getFileIcon(node.name)}
            </div>
          )}
          
          <span className="file-tree-node-name truncate text-xs">{node.name}</span>
        </div>
        
        {node.type === 'folder' && node.isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header aligned with code editor header */}
      <div className="p-4 border-b border-border min-h-[73px] flex items-center">
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-1">
            <Button 
              variant="ghost" 
              size="sm" 
              className="minimalist-button p-1.5 text-[13px]"
              onClick={clearFileTree}
              title="Clear all files"
            >
              <Plus className="h-4 w-4" />
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              className="minimalist-button p-1.5"
              onClick={downloadProject}
              title="Download project"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* File Tree Content */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {fileTree.map(node => renderNode(node))}
        </div>
      </ScrollArea>
    </div>
  );
}