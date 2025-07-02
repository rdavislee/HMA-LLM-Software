// Forward to the vendored tsx binary discovered by initializer
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const tsxBin = process.env.TSX_BIN || path.join(root, '.node_deps', 'node_modules', 'tsx', 'dist', 'cli.mjs');

// Remove stdio: 'inherit' to allow output capture by parent subprocess
const result = spawnSync('node', [tsxBin, ...process.argv.slice(2)]);

// Forward captured output so parent subprocess can see it
if (result.stdout) {
    process.stdout.write(result.stdout);
}
if (result.stderr) {
    process.stderr.write(result.stderr);
}

process.exit(result.status); 