import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { 
  Folder, 
  File, 
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { FileImportService, ImportedNode } from '../services/fileImport';

interface ImportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (nodes: ImportedNode[]) => void;
}

export function ImportDialog({ isOpen, onClose, onImport }: ImportDialogProps) {
  const [isImporting, setIsImporting] = useState(false);
  const [importProgress, setImportProgress] = useState(0);
  const [importStatus, setImportStatus] = useState<'idle' | 'importing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsImporting(true);
    setImportStatus('importing');
    setErrorMessage('');
    setSuccessMessage('');
    setImportProgress(0);

    try {
      const imported = await FileImportService.importFiles(files);
      
      if (imported.length === 0) {
        throw new Error('No valid files found to import');
      }

      setImportProgress(100);
      setImportStatus('success');
      setSuccessMessage(`Successfully imported ${imported.length} file${imported.length > 1 ? 's' : ''}`);
      
      // Pass imported files to parent
      onImport(imported);
      
      // Close dialog after a short delay
      setTimeout(() => {
        onClose();
        resetState();
      }, 1500);
    } catch (error: any) {
      setImportStatus('error');
      setErrorMessage(error.message || 'Failed to import files');
    } finally {
      setIsImporting(false);
    }
  };

  const handleFolderImport = async () => {
    setIsImporting(true);
    setImportStatus('importing');
    setErrorMessage('');
    setSuccessMessage('');
    setImportProgress(20);

    try {
      const folder = await FileImportService.importFolder();
      
      if (!folder) {
        // User cancelled
        resetState();
        return;
      }

      setImportProgress(100);
      setImportStatus('success');
      
      const fileCount = countFiles(folder);
      setSuccessMessage(`Successfully imported ${fileCount} file${fileCount > 1 ? 's' : ''} from "${folder.name}"`);
      
      // Pass imported folder to parent
      onImport([folder]);
      
      // Close dialog after a short delay
      setTimeout(() => {
        onClose();
        resetState();
      }, 1500);
    } catch (error: any) {
      setImportStatus('error');
      setErrorMessage(error.message || 'Failed to import folder');
    } finally {
      setIsImporting(false);
    }
  };

  const countFiles = (node: ImportedNode): number => {
    if (node.type === 'file') return 1;
    return node.children.reduce((count, child) => count + countFiles(child), 0);
  };

  const resetState = () => {
    setImportStatus('idle');
    setImportProgress(0);
    setErrorMessage('');
    setSuccessMessage('');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Import Project</DialogTitle>
          <DialogDescription>
            Import files or an entire folder from your local file system
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Status Messages */}
          {errorMessage && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}
          
          {successMessage && (
            <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
              <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
              <AlertDescription className="text-green-900 dark:text-green-100">
                {successMessage}
              </AlertDescription>
            </Alert>
          )}

          {/* Progress Bar */}
          {importStatus === 'importing' && (
            <div className="space-y-2">
              <Progress value={importProgress} className="h-2" />
              <p className="text-sm text-muted-foreground text-center">
                Importing files...
              </p>
            </div>
          )}

          {/* Import Options */}
          {importStatus === 'idle' && (
            <Tabs defaultValue="files" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="files">Import Files</TabsTrigger>
                <TabsTrigger value="folder">Import Folder</TabsTrigger>
              </TabsList>
              
              <TabsContent value="files" className="space-y-4 mt-4">
                <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
                  <input
                    type="file"
                    multiple
                    onChange={handleFileImport}
                    className="hidden"
                    id="file-input"
                    accept=".js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.h,.cs,.go,.rb,.php,.html,.css,.scss,.sass,.less,.xml,.json,.yaml,.yml,.md,.mdx,.sql,.sh,.bash,.zsh,.fish,.ps1,.r,.R,.swift,.kt,.kts,.dart,.lua,.vim,.dockerfile,.rs,.toml,.ini,.cfg,.conf,.env"
                  />
                  <label
                    htmlFor="file-input"
                    className="cursor-pointer flex flex-col items-center gap-3"
                  >
                    <File className="h-12 w-12 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Click to select files</p>
                      <p className="text-sm text-muted-foreground">
                        Select multiple files to import
                      </p>
                    </div>
                  </label>
                </div>
                
                <p className="text-xs text-muted-foreground text-center">
                  Supported: Source code, configuration files, and text files (max 10MB each)
                </p>
              </TabsContent>
              
              <TabsContent value="folder" className="space-y-4 mt-4">
                <div className="border-2 border-dashed rounded-lg p-8 text-center">
                  <Button
                    onClick={handleFolderImport}
                    disabled={isImporting}
                    className="w-full h-auto py-8 flex flex-col gap-3"
                    variant="outline"
                  >
                    {isImporting ? (
                      <Loader2 className="h-12 w-12 animate-spin" />
                    ) : (
                      <>
                        <Folder className="h-12 w-12" />
                        <div>
                          <p className="font-medium">Select a folder</p>
                          <p className="text-sm font-normal text-muted-foreground">
                            Import an entire project directory
                          </p>
                        </div>
                      </>
                    )}
                  </Button>
                </div>
                
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <p className="font-medium mb-1">Browser Compatibility</p>
                    <p className="text-xs">
                      Folder import requires a Chromium-based browser (Chrome, Edge, Brave, etc.) 
                      with File System Access API support.
                    </p>
                  </AlertDescription>
                </Alert>
              </TabsContent>
            </Tabs>
          )}
        </div>

        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isImporting}
          >
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}