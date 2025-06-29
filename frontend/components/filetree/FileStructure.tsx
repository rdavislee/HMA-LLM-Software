import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen } from 'lucide-react';

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  isOpen?: boolean;
  isModified?: boolean;
  isBeingChanged?: boolean;
  content?: string;
  size?: number;
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
}

const FileTree: React.FC<FileTreeProps> = ({ onFileSelect, importedFiles }) => {
  const [fileStructure, setFileStructure] = useState<FileNode[]>([]);

  // Build file structure from imported files
  useEffect(() => {
    if (importedFiles && importedFiles.length > 0) {
      const newStructure = buildFileStructure(importedFiles);
      setFileStructure(newStructure);
    } else {
      // Fallback to demo structure if no imported files
      setFileStructure([
        {
          name: 'src',
          type: 'folder',
          isOpen: true,
          children: [
            {
              name: 'components',
              type: 'folder',
              isOpen: true,
              children: [
                { name: 'ChatPanel.tsx', type: 'file', isModified: true },
                { name: 'CodePanel.tsx', type: 'file' },
                { name: 'FileTree.tsx', type: 'file', isModified: true },
                { name: 'Terminal.tsx', type: 'file' },
                { name: 'Header.tsx', type: 'file', isModified: true }
              ]
            },
            { name: 'App.tsx', type: 'file' },
            { name: 'main.tsx', type: 'file' },
            { name: 'index.css', type: 'file' }
          ]
        },
        { name: 'package.json', type: 'file', isModified: true },
        { name: 'tailwind.config.js', type: 'file' },
        { name: 'vite.config.ts', type: 'file' }
      ]);
    }
  }, [importedFiles]);

  // Build file structure from imported files
  const buildFileStructure = (files: ImportedFile[]): FileNode[] => {
    const structure: FileNode[] = [];
    const fileMap = new Map<string, FileNode>();

    files.forEach(file => {
      const pathParts = file.path.split('/');
      let currentPath = '';
      
      pathParts.forEach((part, index) => {
        const isLast = index === pathParts.length - 1;
        const isFile = isLast && file.type === 'file';
        
        if (currentPath) {
          currentPath += '/' + part;
        } else {
          currentPath = part;
        }

        if (!fileMap.has(currentPath)) {
          const node: FileNode = {
            name: part,
            type: isFile ? 'file' : 'folder',
            isOpen: true,
            children: isFile ? undefined : [],
            content: isFile ? file.content : undefined,
            size: isFile ? file.size : undefined
          };
          
          fileMap.set(currentPath, node);
          
          // Add to parent or root
          if (index === 0) {
            structure.push(node);
          } else {
            const parentPath = pathParts.slice(0, index).join('/');
            const parent = fileMap.get(parentPath);
            if (parent && parent.children) {
              parent.children.push(node);
            }
          }
        }
      });
    });

    return structure;
  };

  // Simulate real-time file monitoring (in real implementation, this would come from WebSocket)
  useEffect(() => {
    if (fileStructure.length === 0) return;

    // Simulate files being actively changed by the AI model
    const simulateFileChanges = () => {
      setFileStructure(prev => {
        const newStructure = [...prev];
        
        // Simulate random file being actively changed
        const allFiles = getAllFiles(newStructure);
        if (allFiles.length > 0) {
          const randomFile = allFiles[Math.floor(Math.random() * allFiles.length)];
          if (randomFile) {
            // Set the file as being changed
            updateFileStatus(newStructure, randomFile.path, { isBeingChanged: true });
            
            // After 3-8 seconds, mark it as modified and stop being changed
            setTimeout(() => {
              setFileStructure(current => {
                const updatedStructure = [...current];
                updateFileStatus(updatedStructure, randomFile.path, { 
                  isBeingChanged: false, 
                  isModified: true 
                });
                return updatedStructure;
              });
            }, 3000 + Math.random() * 5000);
          }
        }
        
        return newStructure;
      });
    };

    // Start simulation after initial load
    const timer = setTimeout(simulateFileChanges, 2000);
    
    // Set up periodic simulation
    const interval = setInterval(simulateFileChanges, 8000);

    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    };
  }, [fileStructure.length]);

  // Helper function to get all files in the structure
  const getAllFiles = (nodes: FileNode[], path: string[] = []): Array<{ node: FileNode; path: string[] }> => {
    let files: Array<{ node: FileNode; path: string[] }> = [];
    
    for (const node of nodes) {
      const currentPath = [...path, node.name];
      if (node.type === 'file') {
        files.push({ node, path: currentPath });
      } else if (node.children) {
        files = [...files, ...getAllFiles(node.children, currentPath)];
      }
    }
    
    return files;
  };

  // Helper function to update file status
  const updateFileStatus = (nodes: FileNode[], targetPath: string[], updates: Partial<FileNode>) => {
    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i];
      if (node.name === targetPath[0]) {
        if (targetPath.length === 1) {
          // Found the target file/folder
          Object.assign(node, updates);
          return true;
        } else if (node.children) {
          // Continue searching in children
          return updateFileStatus(node.children, targetPath.slice(1), updates);
        }
      }
    }
    return false;
  };

  // Helper function to find file by path
  const findFileByPath = (nodes: FileNode[], targetPath: string[]): FileNode | null => {
    for (const node of nodes) {
      if (node.name === targetPath[0]) {
        if (targetPath.length === 1) {
          return node;
        } else if (node.children) {
          return findFileByPath(node.children, targetPath.slice(1));
        }
      }
    }
    return null;
  };

  const toggleFolder = (path: string[]) => {
    setFileStructure(prev => {
      const newStructure = [...prev];
      let current = newStructure;
      
      for (let i = 0; i < path.length - 1; i++) {
        const folder = current.find(item => item.name === path[i]);
        if (folder?.children) {
          current = folder.children;
        }
      }
      
      const target = current.find(item => item.name === path[path.length - 1]);
      if (target) {
        target.isOpen = !target.isOpen;
      }
      
      return newStructure;
    });
  };

  const handleFileClick = (path: string[]) => {
    const filePath = path.join('/');
    const fileNode = findFileByPath(fileStructure, path);
    onFileSelect?.(filePath, fileNode?.content);
  };

  const renderNode = (node: FileNode, path: string[] = [], depth: number = 0) => {
    const currentPath = [...path, node.name];
    
    // Determine file status and colors
    let fileIconColor = 'text-gray-400'; // Default: unchanged
    let fileNameColor = 'text-gray-300'; // Default: unchanged
    
    if (node.type === 'file') {
      if (node.isBeingChanged) {
        fileIconColor = 'text-yellow-400';
        fileNameColor = 'text-yellow-400';
      } else if (node.isModified) {
        fileIconColor = 'text-green-400';
        fileNameColor = 'text-green-400';
      }
    }
    
    return (
      <div key={currentPath.join('/')}>
        <div
          className={`flex items-center gap-2 px-2 py-1 hover:bg-yellow-400/10 cursor-pointer rounded transition-colors duration-150`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(currentPath);
            } else {
              handleFileClick(currentPath);
            }
          }}
        >
          {node.type === 'folder' ? (
            <>
              {node.isOpen ? (
                <ChevronDown className="w-4 h-4 text-yellow-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-yellow-400" />
              )}
              {node.isOpen ? (
                <FolderOpen className="w-4 h-4 text-yellow-400" />
              ) : (
                <Folder className="w-4 h-4 text-yellow-400" />
              )}
            </>
          ) : (
            <>
              <div className="w-4" />
              <File className={`w-4 h-4 transition-colors ${fileIconColor}`} />
            </>
          )}
          <span className={`text-sm transition-colors ${
            node.type === 'folder' 
              ? 'text-gray-200' 
              : fileNameColor
          }`}>
            {node.name}
          </span>
          {node.type === 'file' && (
            <div className="ml-auto flex items-center gap-1">
              {node.isBeingChanged && (
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
              )}
              {node.isModified && !node.isBeingChanged && (
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              )}
            </div>
          )}
        </div>
        
        {node.type === 'folder' && node.isOpen && node.children && (
          <div>
            {node.children.map(child => renderNode(child, currentPath, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full bg-gray-900 border-r border-yellow-400/20 overflow-y-auto">
      <div className="p-3 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <h3 className="text-yellow-400 font-medium text-sm">PROJECT FILES</h3>
        <div className="flex items-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <span className="text-gray-400">Unchanged</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
            <span className="text-yellow-400">Being Changed</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-green-400">Modified</span>
          </div>
        </div>
      </div>
      <div className="p-2">
        {fileStructure.length > 0 ? (
          fileStructure.map(node => renderNode(node))
        ) : (
          <div className="text-gray-500 text-sm p-4 text-center">
            No files loaded
          </div>
        )}
      </div>
    </div>
  );
};

export default FileTree;
