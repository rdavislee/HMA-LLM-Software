// Forward to the vendored tsc binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const tscBin = process.env.TSC_BIN || path.join(root, '.node_deps', 'node_modules', 'typescript', 'bin', 'tsc');
const result = spawnSync('node', [tscBin, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status); 