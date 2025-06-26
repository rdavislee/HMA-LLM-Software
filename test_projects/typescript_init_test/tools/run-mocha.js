import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import path from 'node:path';

// In ESM context (because package.json may set "type":"module"), we need a CommonJS loader.
// createRequire allows us to use require() and forward to the existing .cjs implementation.

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

require(path.join(__dirname, 'run-mocha.cjs')); 