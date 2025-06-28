// Forward to the vendored ts-node binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const tsNodeBin = process.env.TS_NODE_BIN || path.join(root, '.node_deps', 'node_modules', 'ts-node', 'bin', 'ts-node');
const result = spawnSync('node', [tsNodeBin, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status); 