// Forward to the vendored mocha binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');

// Resolve .node_deps directory – prefer project root, fall back to ancestor directories
function findNodeDeps(startDir) {
  let current = startDir;
  const rootPath = path.parse(current).root;
  while (true) {
    const candidate = path.join(current, '.node_deps', 'node_modules', 'mocha', 'bin', 'mocha.js');
    if (require('node:fs').existsSync(candidate)) {
      return candidate;
    }
    if (current === rootPath) break;
    current = path.dirname(current);
  }
  return null;
}

const projectRoot = path.resolve(__dirname, '..');
const mochaBin = process.env.MOCHA_BIN || findNodeDeps(projectRoot);
if (!mochaBin) {
  console.error('[run-mocha] Could not locate mocha binary in .node_deps. Did the initializer run successfully?');
  process.exit(1);
}

// Add default flags for better test output and detailed error reporting
const defaultFlags = [
  '--reporter', 'spec',          // Use spec reporter for detailed output
  '--no-colors',                 // Disable colors for cleaner agent parsing
  '--bail',                      // Stop on first failure for faster feedback
  '--full-trace',                // Show full stack traces
  '--recursive'                  // Search subdirectories
];

// Combine default flags with any user-provided arguments
const allArgs = [...defaultFlags, ...process.argv.slice(2)];

// Use stdio: 'pipe' to capture output properly for agents
const result = spawnSync('node', [mochaBin, ...allArgs], { 
  stdio: 'pipe',  // Capture stdout/stderr so agents can see detailed test results
  encoding: 'utf8'
});

// Output the captured results to stdout/stderr so subprocess.run() can capture them
if (result.stdout) {
  process.stdout.write(result.stdout);
}
if (result.stderr) {
  process.stderr.write(result.stderr);
}

process.exit(result.status); 