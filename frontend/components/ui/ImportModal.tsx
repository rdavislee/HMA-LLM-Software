import React, { useState, useCallback, useRef, useEffect } from 'react';
import { X, Upload, Folder, File, AlertCircle, CheckCircle, Loader2, FolderOpen } from 'lucide-react';

interface ImportedFile {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  content?: string;
}

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (files: ImportedFile[]) => void;
}

const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onImport
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [importedFiles, setImportedFiles] = useState<ImportedFile[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importMode, setImportMode] = useState<'files' | 'folder'>('files');
  
  // Ref for folder input to set webkitdirectory attribute
  const folderInputRef = useRef<HTMLInputElement>(null);
  
  // Set webkitdirectory attribute directly on mount
  useEffect(() => {
    if (folderInputRef.current) {
      // Set the attribute directly on the DOM element
      folderInputRef.current.setAttribute('webkitdirectory', '');
      folderInputRef.current.setAttribute('directory', '');
      folderInputRef.current.setAttribute('mozdirectory', ''); // For Firefox compatibility
    }
  }, []);

  const validateFile = (file: File): boolean => {
    const validExtensions = [
      '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', '.sass',
      '.json', '.md', '.txt', '.py', '.java', '.cpp', '.c', '.h',
      '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'
    ];
    
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    return validExtensions.includes(extension) || file.type.startsWith('text/');
  };

  const processFiles = useCallback(async (files: FileList | File[]) => {
    const validFiles: ImportedFile[] = [];
    const invalidFiles: string[] = [];
    const processedPaths = new Set<string>();

    console.log('ImportModal: Processing files:', files.length);

    for (const file of Array.from(files)) {
      // For folder imports, webkitRelativePath will contain the full path
      const relativePath = file.webkitRelativePath || file.name;
      
      console.log('ImportModal: Processing file:', {
        name: file.name,
        webkitRelativePath: file.webkitRelativePath,
        relativePath: relativePath,
        type: file.type,
        size: file.size
      });
      
      // Skip if we've already processed this file
      if (processedPaths.has(relativePath)) {
        continue;
      }
      processedPaths.add(relativePath);

      if (validateFile(file)) {
        try {
          const content = await file.text();
          validFiles.push({
            name: file.name,
            path: relativePath,
            type: 'file',
            size: file.size,
            content
          });
        } catch (err) {
          console.error(`Error reading file ${file.name}:`, err);
          invalidFiles.push(file.name);
        }
      } else {
        // For folder imports, we might want to skip non-text files silently
        if (!file.webkitRelativePath) {
          invalidFiles.push(file.name);
        }
      }
    }

    if (invalidFiles.length > 0 && importMode === 'files') {
      setError(`Some files could not be imported: ${invalidFiles.join(', ')}`);
    }

    setImportedFiles(prev => [...prev, ...validFiles]);
    
    // Log for debugging
    console.log('ImportModal: Processed files:', validFiles);
    console.log('ImportModal: Files with paths:', validFiles.map(f => ({ name: f.name, path: f.path })));
  }, [importMode]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setError(null);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFiles(files);
    }
  }, [processFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setError(null);
      processFiles(files);
    }
    // Reset the input to allow selecting the same files again
    e.target.value = '';
  }, [processFiles]);

  // Check browser support for folder selection
  const checkFolderSupport = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    
    // Check if webkitdirectory is supported
    const isSupported = 'webkitdirectory' in input || 'directory' in input || 'mozdirectory' in input;
    
    if (!isSupported && importMode === 'folder') {
      setError('Your browser does not support folder selection. Please use Chrome, Edge, or another Chromium-based browser.');
      return false;
    }
    
    return true;
  }, [importMode]);

  const handleFolderInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    console.log('Folder input triggered, files:', files);
    
    if (files && files.length > 0) {
      setError(null);
      console.log('Processing folder with', files.length, 'files');
      
      // Log first few files to see their paths
      for (let i = 0; i < Math.min(5, files.length); i++) {
        console.log(`File ${i}:`, {
          name: files[i].name,
          webkitRelativePath: files[i].webkitRelativePath,
          size: files[i].size,
          type: files[i].type
        });
      }
      
      processFiles(files);
    } else {
      console.log('No files selected from folder input');
    }
    
    // Reset the input to allow selecting the same folder again
    e.target.value = '';
  }, [processFiles]);

  const handleImport = async () => {
    if (importedFiles.length === 0) {
      setError('Please select files to import');
      return;
    }

    setIsImporting(true);
    setError(null);

    try {
      // Simulate import process
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      onImport(importedFiles);
      onClose();
      setImportedFiles([]);
    } catch (err) {
      setError('Failed to import project. Please try again.');
    } finally {
      setIsImporting(false);
    }
  };

  const removeFile = (index: number) => {
    setImportedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setImportedFiles([]);
    setError(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-yellow-400/20 rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-yellow-400/20">
          <h2 className="text-yellow-400 font-semibold text-xl">Import Project</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Import Mode Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => {
                setImportMode('files');
                setImportedFiles([]);
                setError(null);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                importMode === 'files'
                  ? 'bg-yellow-400/10 text-yellow-400 border border-yellow-400/20'
                  : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
              }`}
            >
              <File className="w-4 h-4" />
              <span>Individual Files</span>
            </button>
            <button
              onClick={() => {
                setImportMode('folder');
                setImportedFiles([]);
                setError(null);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                importMode === 'folder'
                  ? 'bg-yellow-400/10 text-yellow-400 border border-yellow-400/20'
                  : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
              }`}
            >
              <FolderOpen className="w-4 h-4" />
              <span>Entire Folder</span>
            </button>
          </div>

          {/* Drag & Drop Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver
                ? 'border-yellow-400 bg-yellow-400/5'
                : 'border-gray-600 hover:border-yellow-400/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-gray-300 font-medium text-lg mb-2">
              {importMode === 'files' 
                ? 'Drop your project files here'
                : 'Drop your project folder here'
              }
            </h3>
            <p className="text-gray-500 text-sm mb-4">
              {importMode === 'files'
                ? 'Or click to browse files from your computer'
                : 'Or click to browse and select a folder from your computer'
              }
            </p>
            
            {/* File Input */}
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              id="file-input"
              accept=".js,.jsx,.ts,.tsx,.html,.css,.scss,.sass,.json,.md,.txt,.py,.java,.cpp,.c,.h,.php,.rb,.go,.rs,.swift,.kt,.scala"
            />
            
            {/* Folder Input */}
            <input
              type="file"
              webkitdirectory={true}
              directory={true}
              multiple
              onChange={handleFolderInput}
              className="hidden"
              id="folder-input"
              ref={folderInputRef}
            />
            
            <label
              htmlFor={importMode === 'files' ? 'file-input' : 'folder-input'}
              className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors cursor-pointer font-medium"
              onClick={(e) => {
                if (importMode === 'folder' && !checkFolderSupport()) {
                  e.preventDefault();
                }
              }}
            >
              {importMode === 'files' ? (
                <>
                  <File className="w-4 h-4" />
                  Browse Files
                </>
              ) : (
                <>
                  <Folder className="w-4 h-4" />
                  Browse Folder
                </>
              )}
            </label>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-red-400 text-sm">{error}</span>
            </div>
          )}

          {/* Imported Files List */}
          {importedFiles.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-300 font-medium">
                  {importMode === 'files' 
                    ? `Selected Files (${importedFiles.length})`
                    : `Imported Files (${importedFiles.length})`
                  }
                </h3>
                <button
                  onClick={clearAll}
                  className="text-gray-400 hover:text-yellow-400 text-sm transition-colors"
                >
                  Clear All
                </button>
              </div>
              
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {importedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700"
                  >
                    <div className="flex items-center gap-3">
                      {file.type === 'directory' ? (
                        <Folder className="w-4 h-4 text-yellow-400" />
                      ) : (
                        <File className="w-4 h-4 text-yellow-400" />
                      )}
                      <div>
                        <p className="text-gray-300 text-sm font-medium">{file.name}</p>
                        <p className="text-gray-500 text-xs">{file.path}</p>
                        {file.size && (
                          <p className="text-gray-500 text-xs">
                            {(file.size / 1024).toFixed(1)} KB
                          </p>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Supported Formats */}
          <div className="mt-6 p-4 bg-gray-800/30 rounded-lg">
            <h4 className="text-gray-300 font-medium mb-2">Supported Formats</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-gray-400">• JavaScript (.js, .jsx)</div>
              <div className="text-gray-400">• TypeScript (.ts, .tsx)</div>
              <div className="text-gray-400">• HTML (.html)</div>
              <div className="text-gray-400">• CSS (.css, .scss, .sass)</div>
              <div className="text-gray-400">• JSON (.json)</div>
              <div className="text-gray-400">• Markdown (.md)</div>
              <div className="text-gray-400">• Python (.py)</div>
              <div className="text-gray-400">• Java (.java)</div>
              <div className="text-gray-400">• C/C++ (.c, .cpp, .h)</div>
              <div className="text-gray-400">• And more...</div>
            </div>
            {importMode === 'folder' && (
              <p className="text-yellow-400 text-xs mt-2">
                💡 Folder import will include all supported files from the selected directory and its subdirectories
                <br />
                <span className="text-gray-500">Note: Folder selection works in Chrome, Edge, and other Chromium-based browsers</span>
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-yellow-400/20">
          <div className="text-gray-400 text-sm">
            {importedFiles.length > 0 && (
              <span className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                {importedFiles.length} file{importedFiles.length !== 1 ? 's' : ''} ready to import
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-yellow-400 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleImport}
              disabled={importedFiles.length === 0 || isImporting}
              className="flex items-center gap-2 px-4 py-2 bg-yellow-400 hover:bg-yellow-300 disabled:bg-gray-600 disabled:cursor-not-allowed text-black rounded-lg transition-colors font-medium"
            >
              {isImporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Importing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Import Project
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportModal; 
