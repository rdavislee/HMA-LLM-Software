import React, { useState } from 'react';
import { X, Rocket, Code, FileText, AlertCircle } from 'lucide-react';
import { LanguageDropdown } from './index';
import { Language } from '../../src/types';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartProject: (language: Language, prompt: string, projectName?: string) => void;
}

const NewProjectModal: React.FC<NewProjectModalProps> = ({
  isOpen,
  onClose,
  onStartProject
}) => {
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(null);
  const [projectPrompt, setProjectPrompt] = useState('');
  const [projectName, setProjectName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = () => {
    if (!selectedLanguage) {
      setError('Please select a programming language');
      return;
    }

    if (!projectPrompt.trim()) {
      setError('Please describe what you want to build');
      return;
    }

    onStartProject(selectedLanguage, projectPrompt.trim(), projectName.trim() || undefined);
    
    // Reset form
    setSelectedLanguage(null);
    setProjectPrompt('');
    setProjectName('');
    setError(null);
    onClose();
  };

  const handleLanguageChange = (language: Language) => {
    setSelectedLanguage(language);
    setError(null);
  };

  const handleClose = () => {
    // Reset form when closing
    setSelectedLanguage(null);
    setProjectPrompt('');
    setProjectName('');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-yellow-400/20 rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-yellow-400/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-400/10 rounded-lg flex items-center justify-center">
              <Rocket className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <h2 className="text-yellow-400 font-semibold text-xl">New Project</h2>
              <p className="text-gray-400 text-sm">Start building with Hive assistance</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Language Selection */}
          <div>
            <label className="block text-gray-300 font-medium mb-3">
              <Code className="w-4 h-4 inline mr-2" />
              Programming Language
            </label>
            <LanguageDropdown
              onLanguageChange={handleLanguageChange}
            />
            <p className="text-gray-500 text-sm mt-2">
              Choose the primary language for your project
            </p>
          </div>

          {/* Project Description */}
          <div>
            <label className="block text-gray-300 font-medium mb-3">
              <FileText className="w-4 h-4 inline mr-2" />
              Project Description
            </label>
            <textarea
              value={projectPrompt}
              onChange={(e) => {
                setProjectPrompt(e.target.value);
                setError(null);
              }}
              placeholder="Describe what you want to build... For example: 'A task management app with drag-and-drop functionality' or 'A REST API for a blog platform'"
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400 resize-none"
              rows={4}
            />
            <p className="text-gray-500 text-sm mt-2">
              Be as detailed as possible. Hive will ask clarifying questions during Phase 1.
            </p>
          </div>

          {/* Project Name (Optional) */}
          <div>
            <label className="block text-gray-300 font-medium mb-3">
              Project Name <span className="text-gray-500 font-normal">(Optional)</span>
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="my-awesome-project"
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
            />
            <p className="text-gray-500 text-sm mt-2">
              If not provided, a name will be generated automatically
            </p>
          </div>

          {/* Process Overview */}
          <div className="bg-gray-800/50 rounded-lg p-4">
            <h3 className="text-gray-300 font-medium mb-3">What happens next?</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-6 h-6 bg-yellow-400/20 rounded-full flex items-center justify-center text-yellow-400 font-medium">1</div>
                <span className="text-gray-300"><strong>Product Understanding:</strong> Hive asks clarifying questions</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-6 h-6 bg-yellow-400/20 rounded-full flex items-center justify-center text-yellow-400 font-medium">2</div>
                <span className="text-gray-300"><strong>Structure Stage:</strong> Hive creates project structure</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-6 h-6 bg-yellow-400/20 rounded-full flex items-center justify-center text-yellow-400 font-medium">3</div>
                <span className="text-gray-300"><strong>Implementation:</strong> Hive builds your project</span>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-red-400 text-sm">{error}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-yellow-400/20">
          <div className="text-gray-400 text-sm">
            {selectedLanguage && projectPrompt.trim() && (
              <span className="flex items-center gap-2 text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full" />
                Ready to start
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-400 hover:text-yellow-400 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!selectedLanguage || !projectPrompt.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-yellow-400 hover:bg-yellow-300 disabled:bg-gray-600 disabled:cursor-not-allowed text-black rounded-lg transition-colors font-medium"
            >
              <Rocket className="w-4 h-4" />
              Start Project
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewProjectModal;
