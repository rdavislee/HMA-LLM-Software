// File import service for handling local file and folder imports
export interface ImportedFile {
  id: string;
  name: string;
  path: string;
  content: string;
  type: 'file';
  language?: string;
  size: number;
}

export interface ImportedFolder {
  id: string;
  name: string;
  path: string;
  type: 'folder';
  children: (ImportedFile | ImportedFolder)[];
}

export type ImportedNode = ImportedFile | ImportedFolder;

// Supported file extensions with their language mappings
const LANGUAGE_MAP: Record<string, string> = {
  '.js': 'javascript',
  '.jsx': 'javascript',
  '.ts': 'typescript',
  '.tsx': 'typescript',
  '.py': 'python',
  '.java': 'java',
  '.cpp': 'cpp',
  '.c': 'c',
  '.h': 'c',
  '.cs': 'csharp',
  '.go': 'go',
  '.rb': 'ruby',
  '.php': 'php',
  '.html': 'html',
  '.css': 'css',
  '.scss': 'scss',
  '.sass': 'sass',
  '.less': 'less',
  '.xml': 'xml',
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.md': 'markdown',
  '.mdx': 'markdown',
  '.sql': 'sql',
  '.sh': 'bash',
  '.bash': 'bash',
  '.zsh': 'bash',
  '.fish': 'bash',
  '.ps1': 'powershell',
  '.r': 'r',
  '.R': 'r',
  '.swift': 'swift',
  '.kt': 'kotlin',
  '.kts': 'kotlin',
  '.dart': 'dart',
  '.lua': 'lua',
  '.vim': 'vim',
  '.dockerfile': 'dockerfile',
  '.rs': 'rust',
  '.toml': 'toml',
  '.ini': 'ini',
  '.cfg': 'ini',
  '.conf': 'ini',
  '.env': 'dotenv',
};

// File size limit (10MB)
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Binary file extensions to skip
const BINARY_EXTENSIONS = new Set([
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  '.zip', '.rar', '.tar', '.gz', '.7z',
  '.exe', '.dll', '.so', '.dylib',
  '.mp3', '.mp4', '.avi', '.mov', '.wav',
  '.ttf', '.otf', '.woff', '.woff2',
  '.db', '.sqlite',
]);

// Folders to skip
const SKIP_FOLDERS = new Set([
  'node_modules',
  '.git',
  '.svn',
  '.hg',
  'dist',
  'build',
  'out',
  'target',
  'bin',
  'obj',
  '.idea',
  '.vscode',
  '.vs',
  '__pycache__',
  '.pytest_cache',
  '.mypy_cache',
  'venv',
  'env',
  '.env',
]);

export class FileImportService {
  /**
   * Import a single file
   */
  static async importFile(file: File): Promise<ImportedFile | null> {
    try {
      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        throw new Error(`File "${file.name}" exceeds the maximum size of 10MB`);
      }

      const extension = this.getFileExtension(file.name);
      
      // Skip binary files
      if (BINARY_EXTENSIONS.has(extension.toLowerCase())) {
        console.warn(`Skipping binary file: ${file.name}`);
        return null;
      }

      // Read file content
      const content = await this.readFileAsText(file);
      
      return {
        id: this.generateId(),
        name: file.name,
        path: file.name,
        content,
        type: 'file',
        language: this.getLanguageFromExtension(extension),
        size: file.size,
      };
    } catch (error) {
      console.error(`Error importing file ${file.name}:`, error);
      return null;
    }
  }

  /**
   * Import multiple files
   */
  static async importFiles(files: FileList): Promise<ImportedFile[]> {
    const imported: ImportedFile[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (!file) continue;
      const importedFile = await this.importFile(file);
      if (importedFile) {
        imported.push(importedFile);
      }
    }
    
    return imported;
  }

  /**
   * Import a folder using File System Access API
   */
  static async importFolder(): Promise<ImportedFolder | null> {
    try {
      // Check if File System Access API is supported
      if (!('showDirectoryPicker' in window)) {
        throw new Error('Your browser does not support folder import. Please use Chrome, Edge, or another Chromium-based browser.');
      }

      // Request directory access
      const dirHandle = await (window as any).showDirectoryPicker({
        mode: 'read',
      });

      // Read directory contents
      const rootFolder = await this.readDirectory(dirHandle, dirHandle.name);
      return rootFolder;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // User cancelled the picker
        return null;
      }
      console.error('Error importing folder:', error);
      throw error;
    }
  }

  /**
   * Recursively read directory contents
   */
  private static async readDirectory(
    dirHandle: any,
    path: string,
    depth: number = 0,
    maxDepth: number = 10
  ): Promise<ImportedFolder> {
    const folder: ImportedFolder = {
      id: this.generateId(),
      name: dirHandle.name,
      path,
      type: 'folder',
      children: [],
    };

    // Prevent infinite recursion
    if (depth > maxDepth) {
      console.warn(`Max depth reached for folder: ${path}`);
      return folder;
    }

    // Skip certain folders
    if (SKIP_FOLDERS.has(dirHandle.name)) {
      console.log(`Skipping folder: ${dirHandle.name}`);
      return folder;
    }

    try {
      // Iterate through directory entries
      for await (const entry of dirHandle.values()) {
        const entryPath = `${path}/${entry.name}`;

        if (entry.kind === 'file') {
          const file = await entry.getFile();
          if (!file) continue;
          
          // Skip large files
          if (file.size > MAX_FILE_SIZE) {
            console.warn(`Skipping large file: ${entryPath} (${file.size} bytes)`);
            continue;
          }

          const extension = this.getFileExtension(file.name);
          
          // Skip binary files
          if (BINARY_EXTENSIONS.has(extension.toLowerCase())) {
            console.log(`Skipping binary file: ${entryPath}`);
            continue;
          }

          try {
            const content = await this.readFileAsText(file);
            folder.children.push({
              id: this.generateId(),
              name: file.name,
              path: entryPath,
              content,
              type: 'file',
              language: this.getLanguageFromExtension(extension),
              size: file.size,
            });
          } catch (error) {
            console.error(`Error reading file ${entryPath}:`, error);
          }
        } else if (entry.kind === 'directory') {
          // Skip certain folders
          if (!SKIP_FOLDERS.has(entry.name)) {
            const subFolder = await this.readDirectory(entry, entryPath, depth + 1, maxDepth);
            if (subFolder.children.length > 0) {
              folder.children.push(subFolder);
            }
          }
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${path}:`, error);
    }

    // Sort children: folders first, then files, alphabetically
    folder.children.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'folder' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });

    return folder;
  }

  /**
   * Read file as text
   */
  private static async readFileAsText(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  /**
   * Get file extension
   */
  private static getFileExtension(filename: string): string {
    const lastDot = filename.lastIndexOf('.');
    return lastDot === -1 ? '' : filename.substring(lastDot);
  }

  /**
   * Get language from file extension
   */
  private static getLanguageFromExtension(extension: string): string {
    return LANGUAGE_MAP[extension.toLowerCase()] || 'plaintext';
  }

  /**
   * Generate unique ID
   */
  private static generateId(): string {
    return `import-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Convert imported structure to FileTree format
   */
  static convertToFileTreeNodes(imported: ImportedNode[]): any[] {
    return imported.map(node => this.convertNode(node));
  }

  private static convertNode(node: ImportedNode): any {
    if (node.type === 'file') {
      return {
        id: node.id,
        name: node.name,
        path: node.path,
        type: 'file',
        content: node.content,
        language: node.language,
      };
    } else {
      return {
        id: node.id,
        name: node.name,
        path: node.path,
        type: 'folder',
        children: node.children.map(child => this.convertNode(child)),
        isExpanded: false,
      };
    }
  }
}