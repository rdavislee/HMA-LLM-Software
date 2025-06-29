/// <reference types="react" />

declare module 'react' {
  interface InputHTMLAttributes<T> extends React.HTMLAttributes<T> {
    webkitdirectory?: boolean;
    directory?: boolean;
  }
} 