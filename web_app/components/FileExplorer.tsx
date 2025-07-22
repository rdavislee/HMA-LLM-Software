import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { 
  Search, 
  Folder, 
  File, 
  FileText, 
  Code, 
  Image, 
  Settings,
  ChevronRight,
  ChevronDown,
  Plus
} from 'lucide-react';

interface FileNode {
  id: string;
  name: string;
  type: 'folder' | 'file';
  children?: FileNode[];
  extension?: string;
  isExpanded?: boolean;
}

export function FileExplorer() {
  const [fileTree, setFileTree] = useState<FileNode[]>([
    {
      id: '1',
      name: 'src',
      type: 'folder',
      isExpanded: true,
      children: [
        {
          id: '2',
          name: 'components',
          type: 'folder',
          isExpanded: true,
          children: [
            { id: '3', name: 'Button.tsx', type: 'file', extension: 'tsx' },
            { id: '4', name: 'Modal.tsx', type: 'file', extension: 'tsx' },
            { id: '5', name: 'Form.tsx', type: 'file', extension: 'tsx' }
          ]
        },
        {
          id: '6',
          name: 'utils',
          type: 'folder',
          isExpanded: false,
          children: [
            { id: '7', name: 'helpers.ts', type: 'file', extension: 'ts' },
            { id: '8', name: 'constants.ts', type: 'file', extension: 'ts' }
          ]
        },
        { id: '9', name: 'App.tsx', type: 'file', extension: 'tsx' },
        { id: '10', name: 'index.tsx', type: 'file', extension: 'tsx' }
      ]
    },
    {
      id: '11',
      name: 'public',
      type: 'folder',
      isExpanded: false,
      children: [
        { id: '12', name: 'index.html', type: 'file', extension: 'html' },
        { id: '13', name: 'favicon.ico', type: 'file', extension: 'ico' }
      ]
    },
    { id: '14', name: 'package.json', type: 'file', extension: 'json' },
    { id: '15', name: 'README.md', type: 'file', extension: 'md' }
  ]);

  const [selectedFile, setSelectedFile] = useState<string | null>('3');

  const toggleFolder = (id: string) => {
    const updateNode = (nodes: FileNode[]): FileNode[] => {
      return nodes.map(node => {
        if (node.id === id) {
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

  const getFileIcon = (extension?: string) => {
    switch (extension) {
      case 'tsx':
      case 'ts':
      case 'js':
      case 'jsx':
        return <Code className="h-3 w-3 text-blue-400" />;
      case 'html':
      case 'css':
        return <FileText className="h-3 w-3 text-orange-400" />;
      case 'json':
        return <FileText className="h-3 w-3 text-yellow-400" />;
      case 'md':
        return <FileText className="h-3 w-3 text-green-400" />;
      case 'ico':
      case 'png':
      case 'jpg':
      case 'svg':
        return <Image className="h-3 w-3 text-purple-400" />;
      default:
        return <File className="h-3 w-3 text-gray-400" />;
    }
  };

  const renderFileTree = (nodes: FileNode[], level: number = 0) => {
    return nodes.map((node) => (
      <div key={node.id}>
        <div 
          className={`flex items-center gap-1 px-1 py-1 rounded cursor-pointer hover:bg-secondary/50 transition-colors ${
            selectedFile === node.id ? 'bg-secondary' : ''
          }`}
          style={{ paddingLeft: `${level * 8 + 4}px` }}
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(node.id);
            } else {
              setSelectedFile(node.id);
            }
          }}
        >
          {node.type === 'folder' ? (
            <>
              {node.isExpanded ? (
                <ChevronDown className="h-3 w-3 text-muted-foreground flex-shrink-0" />
              ) : (
                <ChevronRight className="h-3 w-3 text-muted-foreground flex-shrink-0" />
              )}
              <Folder className="h-3 w-3 text-blue-400 flex-shrink-0" />
            </>
          ) : (
            <>
              <div className="w-3 flex-shrink-0" />
              {getFileIcon(node.extension)}
            </>
          )}
          
          <span className="flex-1 text-xs truncate">{node.name}</span>
        </div>
        
        {node.type === 'folder' && node.isExpanded && node.children && (
          <div>
            {renderFileTree(node.children, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="h-full bg-card border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-border">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium text-sm">Files</h3>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
              <Plus className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
              <Settings className="h-3 w-3" />
            </Button>
          </div>
        </div>
        
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground" />
          <Input
            placeholder="Search..."
            className="pl-7 h-7 text-xs bg-input-background"
          />
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto p-1">
        <div className="space-y-0.5">
          {renderFileTree(fileTree)}
        </div>
      </div>
    </div>
  );
}