// Forward to the vendored mocha binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const mochaBin = process.env.MOCHA_BIN || path.join(root, '.node_deps', 'node_modules', 'mocha', 'bin', 'mocha');
const result = spawnSync('node', [mochaBin, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status); 