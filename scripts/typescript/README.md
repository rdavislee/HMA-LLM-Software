# TypeScript Environment Initializer

This folder contains everything needed to set up a **fully offline, portable TypeScript development environment** for agent sandboxes and test projects.

## What does this do?
- **Installs TypeScript, ts-node, tsx, mocha, chai, and type definitions** from pre-downloaded npm tarballs (in `npm-packages/`) into a local `.node_deps` directory inside the target project.
- **Bootstraps Node.js/npm automatically** if they are not available on the system:
  - Downloads the official Node.js binary for Windows, Mac, or Linux.
  - Extracts it to `scripts/typescript/nodejs/`.
  - Uses this local Node.js/npm for all install commands.
- **No network access is required** after the initial Node.js download. All TypeScript tooling is installed from local tarballs.

## How does it work?
- The main entry point is `initializer.py`.
- When run (usually by the main project initializer), it:
  1. Checks if `.node_deps/node_modules/typescript` exists in the target project. If so, does nothing.
  2. Checks for `npm` in the system `PATH`.
  3. If not found, downloads and extracts Node.js for the current OS.
  4. Installs all `.tgz` tarballs from `npm-packages/` into `.node_deps` using the available (system or local) npm.

## Why?
- **Agents run in a sandbox with no network access.**
- This lets them compile, run, and test TypeScript code using only pre-vendored tools.
- No global Node.js/npm installation is required for users or CI.

## Directory structure
- `npm-packages/` — Pre-downloaded npm tarballs for all required TypeScript tooling.
- `nodejs/` — (Auto-created) Local Node.js binary for your OS, if needed.
- `initializer.py` — The main setup script.

## Supported platforms
- Windows (x64)
- Mac (x64)
- Linux (x64)

## Adding/Updating Packages
1. On a machine with internet access, run:
   ```sh
   npm pack typescript@<version> ts-node@<version> tsx@<version> ...
   ```
2. Copy the resulting `.tgz` files into `npm-packages/`.

## Troubleshooting
- If you see errors about `npm` not found, the script will attempt to download Node.js/npm for you.
- If you have a custom Node.js/npm install, make sure it is in your `PATH`.

---

**This system ensures that all TypeScript development and testing can be done 100% offline and reproducibly, regardless of the host machine's setup.** 