// Forward to the vendored ts-node binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const tsNodeBin = process.env.TS_NODE_BIN || path.join(root, '.node_deps', 'node_modules', 'ts-node', 'dist', 'bin.js');

// Remove stdio: 'inherit' to allow output capture by parent subprocess
const result = spawnSync('node', [tsNodeBin, ...process.argv.slice(2)]);

// Forward captured output so parent subprocess can see it
if (result.stdout) {
    process.stdout.write(result.stdout);
}
if (result.stderr) {
    process.stderr.write(result.stderr);
}

process.exit(result.status); 