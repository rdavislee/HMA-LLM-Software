import React from 'react';
import { describe, it, expect, beforeEach, vi } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '../../setup/testUtils';
import { FileTree } from '@/components/FileTree';
import { useSocketEvent } from '@/hooks/useSocketEvent';
import websocketService from '@/services/websocket';

// Mock dependencies
jest.mock('@/hooks/useSocketEvent');
jest.mock('@/services/websocket');

describe('FileTree Component', () => {
  const mockUseSocketEvent = useSocketEvent as jest.MockedFunction<typeof useSocketEvent>;
  const mockWebSocketService = websocketService as jest.Mocked<typeof websocketService>;
  const mockOnFileSelect = jest.fn();

  const mockFileStructure = {
    name: 'root',
    type: 'folder' as const,
    children: [
      {
        name: 'src',
        type: 'folder' as const,
        children: [
          { name: 'index.ts', type: 'file' as const, path: '/src/index.ts' },
          { name: 'utils.ts', type: 'file' as const, path: '/src/utils.ts' },
          {
            name: 'components',
            type: 'folder' as const,
            children: [
              { name: 'Button.tsx', type: 'file' as const, path: '/src/components/Button.tsx' },
              { name: 'Input.tsx', type: 'file' as const, path: '/src/components/Input.tsx' },
            ]
          }
        ]
      },
      { name: 'README.md', type: 'file' as const, path: '/README.md' },
      { name: 'package.json', type: 'file' as const, path: '/package.json' },
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSocketEvent.mockImplementation(() => {});
  });

  describe('Rendering', () => {
    it('should render file tree container', () => {
      render(<FileTree onFileSelect={mockOnFileSelect} />);
      
      expect(screen.getByText('Files')).toBeInTheDocument();
    });

    it('should render with initial files', () => {
      render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      expect(screen.getByText('src')).toBeInTheDocument();
      expect(screen.getByText('README.md')).toBeInTheDocument();
      expect(screen.getByText('package.json')).toBeInTheDocument();
    });

    it('should show empty state when no files', () => {
      render(<FileTree onFileSelect={mockOnFileSelect} />);
      
      expect(screen.getByText('No files available')).toBeInTheDocument();
    });
  });

  describe('File Tree Interactions', () => {
    it('should expand and collapse folders', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const srcFolder = screen.getByText('src');
      
      // Initially collapsed - children not visible
      expect(screen.queryByText('index.ts')).not.toBeInTheDocument();
      
      // Click to expand
      await user.click(srcFolder);
      
      // Children should be visible
      expect(screen.getByText('index.ts')).toBeInTheDocument();
      expect(screen.getByText('utils.ts')).toBeInTheDocument();
      expect(screen.getByText('components')).toBeInTheDocument();
      
      // Click to collapse
      await user.click(srcFolder);
      
      // Children should be hidden
      expect(screen.queryByText('index.ts')).not.toBeInTheDocument();
    });

    it('should expand nested folders', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      // Expand src
      await user.click(screen.getByText('src'));
      
      // Expand components
      await user.click(screen.getByText('components'));
      
      // Nested files should be visible
      expect(screen.getByText('Button.tsx')).toBeInTheDocument();
      expect(screen.getByText('Input.tsx')).toBeInTheDocument();
    });

    it('should select files on click', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      // Click on README.md
      await user.click(screen.getByText('README.md'));
      
      expect(mockOnFileSelect).toHaveBeenCalledWith('/README.md');
      expect(mockWebSocketService.selectFile).toHaveBeenCalledWith('/README.md');
    });

    it('should select nested files', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      // Expand folders
      await user.click(screen.getByText('src'));
      await user.click(screen.getByText('components'));
      
      // Select nested file
      await user.click(screen.getByText('Button.tsx'));
      
      expect(mockOnFileSelect).toHaveBeenCalledWith('/src/components/Button.tsx');
    });

    it('should highlight selected file', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const readmeFile = screen.getByText('README.md');
      
      // Initially not selected
      expect(readmeFile.parentElement).not.toHaveClass('bg-accent');
      
      // Click to select
      await user.click(readmeFile);
      
      // Should be highlighted
      expect(readmeFile.parentElement).toHaveClass('bg-accent');
    });

    it('should change selection between files', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      // Select first file
      await user.click(screen.getByText('README.md'));
      expect(screen.getByText('README.md').parentElement).toHaveClass('bg-accent');
      
      // Select second file
      await user.click(screen.getByText('package.json'));
      
      // First file should not be selected anymore
      expect(screen.getByText('README.md').parentElement).not.toHaveClass('bg-accent');
      // Second file should be selected
      expect(screen.getByText('package.json').parentElement).toHaveClass('bg-accent');
    });
  });

  describe('WebSocket Integration', () => {
    it('should register file tree update listener', () => {
      render(<FileTree onFileSelect={mockOnFileSelect} />);
      
      expect(mockUseSocketEvent).toHaveBeenCalledWith(
        'file_tree_update',
        expect.any(Function)
      );
    });

    it('should update file tree from WebSocket', async () => {
      let updateHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'file_tree_update') {
          updateHandler = handler;
        }
      });

      render(<FileTree onFileSelect={mockOnFileSelect} />);
      
      // Initially empty
      expect(screen.getByText('No files available')).toBeInTheDocument();
      
      // Send update
      updateHandler(mockFileStructure);
      
      await waitFor(() => {
        expect(screen.getByText('src')).toBeInTheDocument();
        expect(screen.getByText('README.md')).toBeInTheDocument();
      });
    });

    it('should preserve expansion state on updates', async () => {
      let updateHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'file_tree_update') {
          updateHandler = handler;
        }
      });

      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect}
          initialFiles={mockFileStructure}
        />
      );
      
      // Expand src folder
      await user.click(screen.getByText('src'));
      expect(screen.getByText('index.ts')).toBeInTheDocument();
      
      // Update with new file structure
      const updatedStructure = {
        ...mockFileStructure,
        children: [
          ...mockFileStructure.children,
          { name: 'new-file.ts', type: 'file' as const, path: '/new-file.ts' }
        ]
      };
      
      updateHandler(updatedStructure);
      
      await waitFor(() => {
        // src should still be expanded
        expect(screen.getByText('index.ts')).toBeInTheDocument();
        // New file should appear
        expect(screen.getByText('new-file.ts')).toBeInTheDocument();
      });
    });
  });

  describe('File Icons', () => {
    it('should show folder icons', () => {
      const { container } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const folderIcons = container.querySelectorAll('.lucide-folder');
      expect(folderIcons.length).toBeGreaterThan(0);
    });

    it('should show file icons', () => {
      const { container } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const fileIcons = container.querySelectorAll('.lucide-file');
      expect(fileIcons.length).toBeGreaterThan(0);
    });

    it('should show chevron for folders', () => {
      const { container } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const chevronIcons = container.querySelectorAll('.lucide-chevron-right');
      expect(chevronIcons.length).toBeGreaterThan(0);
    });

    it('should rotate chevron when expanded', async () => {
      const { user, container } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const srcFolder = screen.getByText('src');
      const chevron = srcFolder.parentElement?.querySelector('.lucide-chevron-right');
      
      expect(chevron).not.toHaveClass('rotate-90');
      
      await user.click(srcFolder);
      
      expect(chevron).toHaveClass('rotate-90');
    });
  });

  describe('Styling', () => {
    it('should apply hover styles', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      const readmeFile = screen.getByText('README.md');
      
      // Hover over file
      await user.hover(readmeFile);
      
      expect(readmeFile.parentElement).toHaveClass('hover:bg-accent/50');
    });

    it('should indent nested items', async () => {
      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={mockFileStructure}
        />
      );
      
      // Expand to see nested items
      await user.click(screen.getByText('src'));
      
      const nestedFile = screen.getByText('index.ts');
      const parentFolder = screen.getByText('src');
      
      // Nested items should have additional padding
      expect(nestedFile.parentElement?.parentElement).toHaveClass('pl-4');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty folders', async () => {
      const emptyFolderStructure = {
        name: 'root',
        type: 'folder' as const,
        children: [
          {
            name: 'empty-folder',
            type: 'folder' as const,
            children: []
          }
        ]
      };

      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={emptyFolderStructure}
        />
      );
      
      // Click on empty folder
      await user.click(screen.getByText('empty-folder'));
      
      // Should not crash and folder should be expandable
      expect(screen.getByText('empty-folder')).toBeInTheDocument();
    });

    it('should handle files without paths', () => {
      const noPathStructure = {
        name: 'root',
        type: 'folder' as const,
        children: [
          { name: 'no-path.txt', type: 'file' as const }
        ]
      };

      render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={noPathStructure}
        />
      );
      
      expect(screen.getByText('no-path.txt')).toBeInTheDocument();
    });

    it('should handle deeply nested structures', async () => {
      const deepStructure = {
        name: 'root',
        type: 'folder' as const,
        children: [{
          name: 'level1',
          type: 'folder' as const,
          children: [{
            name: 'level2',
            type: 'folder' as const,
            children: [{
              name: 'level3',
              type: 'folder' as const,
              children: [{
                name: 'deep-file.txt',
                type: 'file' as const,
                path: '/level1/level2/level3/deep-file.txt'
              }]
            }]
          }]
        }]
      };

      const { user } = render(
        <FileTree 
          onFileSelect={mockOnFileSelect} 
          initialFiles={deepStructure}
        />
      );
      
      // Expand all levels
      await user.click(screen.getByText('level1'));
      await user.click(screen.getByText('level2'));
      await user.click(screen.getByText('level3'));
      
      // Deep file should be visible and selectable
      const deepFile = screen.getByText('deep-file.txt');
      expect(deepFile).toBeInTheDocument();
      
      await user.click(deepFile);
      expect(mockOnFileSelect).toHaveBeenCalledWith('/level1/level2/level3/deep-file.txt');
    });
  });
});