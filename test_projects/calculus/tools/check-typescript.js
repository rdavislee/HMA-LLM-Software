// TypeScript checker - shows errors and warnings without compilation
// This tool runs `tsc --noEmit` to provide diagnostics similar to IDE "red squiggles"
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const tscBin = process.env.TSC_BIN || path.join(root, '.node_deps', 'node_modules', 'typescript', 'bin', 'tsc');

// Run TypeScript compiler in check-only mode (no output files generated)
// Remove stdio: 'inherit' to allow output capture by parent subprocess
const result = spawnSync('node', [tscBin, '--noEmit', ...process.argv.slice(2)]);

// Forward captured output so parent subprocess can see it
if (result.stdout) {
    process.stdout.write(result.stdout);
}
if (result.stderr) {
    process.stderr.write(result.stderr);
}

process.exit(result.status); 