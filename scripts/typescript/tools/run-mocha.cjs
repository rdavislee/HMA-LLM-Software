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

const result = spawnSync('node', [mochaBin, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status); 