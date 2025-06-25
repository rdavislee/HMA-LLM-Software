## Initializer: Setting up Mocha for Agents

The agents execute in a restricted sandbox that has **no network access**. In order for them to run JavaScript / TypeScript test-suites with Mocha we need to pre-install (or vendor) Mocha and expose a deterministic test command before any agent starts.  The general flow is:

1. **Ship Mocha in the repository**
   - On a machine with Internet access run:
     ```bash
     npm pack mocha@10.2.0
     npm pack chai@4.3.8
     npm pack ts-node@10.9.1        # only if .ts test files need transpilation
     ```
   - Commit the resulting tarballs (e.g. `mocha-10.2.0.tgz`) to `tools/npm-packages/`.

2. **Add an installation helper**
   Create `scripts/install_local_mocha.py`:
   ```python
   #!/usr/bin/env python3
   """Extract locally-cached *.tgz packages into <workspace>/.node_deps."""
   import subprocess, pathlib, sys

   root = pathlib.Path(__file__).resolve().parent.parent
   cache_dir = root / ".node_deps"
   cache_dir.mkdir(exist_ok=True)

   # Install all vendored tarballs in one go (no registry access needed)
   subprocess.run([
       "npm", "install", "--prefix", str(cache_dir),
       *map(str, (root / "tools" / "npm-packages").glob("*.tgz"))
   ], check=True)
   ```

3. **Wire the helper into the project initializer** (`src/initializer.py`):
   ```python
   from pathlib import Path
   import subprocess

   def _ensure_node_deps():
       project_root = Path(__file__).resolve().parent.parent
       node_deps = project_root / ".node_deps" / "node_modules"
       if not (node_deps / "mocha").exists():
           subprocess.run(["python", "scripts/install_local_mocha.py"], check=True)
       return node_deps

   # make MOCHA_BIN available globally (path str)
   MOCHA_BIN = str(_ensure_node_deps() / "mocha" / "bin" / "mocha")
   ```

4. **Expose a single offline test command**
   - Add `tools/run-mocha.js`:
     ```js
     // Forward to the vendored mocha binary discovered by initializer
     const { spawnSync } = require('node:child_process');
     const path = require('node:path');
     const root = path.resolve(__dirname, '..');
     const mochaBin = process.env.MOCHA_BIN || path.join(root, '.node_deps', 'node_modules', 'mocha', 'bin', 'mocha');
     const result = spawnSync('node', [mochaBin, ...process.argv.slice(2)], { stdio: 'inherit' });
     process.exit(result.status);
     ```
   - Update `prompts/*/available_commands.md` so agents run:
     ```
     RUN "node tools/run-mocha.js test/**/*.test.js"
     ```
     rather than `npm test`.

5. **Remove `npm install` and `npm test` from `ALLOWED_COMMANDS`**
   This prevents agents from falling back to network-bound commands.

With these steps the first time the workspace starts the initializer will unpack the vendored tarballs; afterwards agents can execute Mocha completely offline via the stable wrapper script.
