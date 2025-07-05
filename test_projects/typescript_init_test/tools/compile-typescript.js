// Forward to the vendored tsc binary discovered by initializer
// Enhanced to show code context around errors
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

const root = path.resolve(__dirname, '..');
const tscBin = process.env.TSC_BIN || path.join(root, '.node_deps', 'node_modules', 'typescript', 'bin', 'tsc');

// Run TypeScript compiler with enhanced error reporting
const result = spawnSync('node', [tscBin, ...process.argv.slice(2)], {
    encoding: 'utf8'
});

// Parse TypeScript error output and enhance with code context
function enhanceErrorOutput(errorOutput) {
    if (!errorOutput) return '';
    
    const lines = errorOutput.split('\n');
    let enhancedOutput = '';
    
    for (const line of lines) {
        // Match TypeScript error format: file(line,column): error TScode: message
        // Handle carriage returns by trimming the line
        const cleanLine = line.replace(/\r$/, '');
        const errorMatch = cleanLine.match(/^(.+?)\((\d+),(\d+)\):\s*(error|warning)\s*(TS\d+):\s*(.+)$/);
        
        if (errorMatch) {
            const [, filePath, lineNum, columnNum, severity, errorCode, message] = errorMatch;
            const lineNumber = parseInt(lineNum);
            const columnNumber = parseInt(columnNum);
            
            // Add the original error line
            enhancedOutput += line + '\n';
            
            // Try to read the file and show context
            try {
                const fullPath = path.resolve(root, filePath);
                if (fs.existsSync(fullPath)) {
                    const fileContent = fs.readFileSync(fullPath, 'utf8');
                    const fileLines = fileContent.split('\n');
                    
                    // Show context around the error (3 lines before and after)
                    const contextStart = Math.max(0, lineNumber - 4);
                    const contextEnd = Math.min(fileLines.length, lineNumber + 3);
                    
                    enhancedOutput += '\n  Code context:\n';
                    
                    for (let i = contextStart; i < contextEnd; i++) {
                        const displayLineNum = (i + 1).toString().padStart(4, ' ');
                        const isErrorLine = (i + 1) === lineNumber;
                        const lineContent = fileLines[i] || '';
                        
                        if (isErrorLine) {
                            enhancedOutput += `  > ${displayLineNum} | ${lineContent}\n`;
                            
                            // Add pointer to the specific column
                            const spaces = ' '.repeat(columnNumber - 1);
                            const pointer = '^'.repeat(Math.max(1, 3)); // Show a few chars for visibility
                            enhancedOutput += `  ${' '.repeat(8)} | ${spaces}${pointer}\n`;
                        } else {
                            enhancedOutput += `    ${displayLineNum} | ${lineContent}\n`;
                        }
                    }
                    enhancedOutput += '\n';
                }
            } catch (err) {
                // If we can't read the file, just show the original error
                enhancedOutput += `  (Could not read source file for context)\n\n`;
            }
        } else {
            // Not an error line, just pass through
            enhancedOutput += line + '\n';
        }
    }
    
    return enhancedOutput;
}

// Enhance and output the results
if (result.stdout) {
    const enhanced = enhanceErrorOutput(result.stdout);
    process.stdout.write(enhanced);
}

if (result.stderr) {
    const enhanced = enhanceErrorOutput(result.stderr);
    process.stderr.write(enhanced);
}

process.exit(result.status); 