// Forward to the vendored tsx binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const tsxBin = process.env.TSX_BIN || path.join(root, '.node_deps', 'node_modules', 'tsx', 'dist', 'cli.mjs');
const result = spawnSync('node', [tsxBin, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status); 