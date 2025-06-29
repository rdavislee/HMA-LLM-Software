// Type definitions for webkit directory upload features
interface HTMLInputElement {
  webkitdirectory?: boolean;
  directory?: boolean;
  mozdirectory?: boolean;
}

interface File {
  webkitRelativePath?: string;
}

// For JSX attributes
declare namespace React {
  interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    webkitdirectory?: boolean;
    directory?: boolean;
    mozdirectory?: boolean;
  }
} 