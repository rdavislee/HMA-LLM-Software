/// <reference types="vite/client" />

// Extend HTMLInputElement to include webkitdirectory attribute
declare global {
  interface HTMLInputElement {
    webkitdirectory: boolean;
  }
}
