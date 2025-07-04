import { expect } from 'chai';
import { extractVariables, isValidNumericInput } from '../src/cli'; // Assuming these helpers are exported from src/cli.ts

describe('CLI Helper Functions', () => {

    describe('extractVariables()', () => {
        it('should return an empty array for an empty expression', () => {
            expect(extractVariables('')).to.deep.equal([]);
        });

        it('should return an empty array for an expression with only whitespace', () => {
            expect(extractVariables('   ')).to.deep.equal([]);
        });

        it('should return an empty array for an expression with no variables', () => {
            expect(extractVariables('2 + 3 * 4')).to.deep.equal([]);
            expect(extractVariables('sin(pi/2) + log(10)')).to.deep.equal([]); // Built-in functions/constants
        });

        it('should extract a single variable', () => {
            expect(extractVariables('x + 5')).to.deep.equal(['x']);
        });

        it('should extract multiple unique variables', () => {
            expect(extractVariables('a + b - c')).to.deep.equal(['a', 'b', 'c'].sort());
        });

        it('should handle repeated variables and return unique ones', () => {
            expect(extractVariables('x + y - x * z')).to.deep.equal(['x', 'y', 'z'].sort());
        });

        it('should handle variables with numbers', () => {
            expect(extractVariables('x1 + y2 / z3')).to.deep.equal(['x1', 'y2', 'z3'].sort());
        });

        it('should extract variables from complex expressions', () => {
            expect(extractVariables('(a + b) * sin(c) / d')).to.deep.equal(['a', 'b', 'c', 'd'].sort());
            expect(extractVariables('log(x, 2) + y^z')).to.deep.equal(['x', 'y', 'z'].sort());
        });

        it('should not extract built-in mathjs functions as variables', () => {
            expect(extractVariables('sin(x) + cos(y)')).to.deep.equal(['x', 'y'].sort());
            expect(extractVariables('abs(val) + sqrt(another)')).to.deep.equal(['another', 'val'].sort());
        });

        it('should not extract built-in mathjs constants as variables', () => {
            expect(extractVariables('pi + e + x')).to.deep.equal(['x']);
            expect(extractVariables('pi')).to.deep.equal([]);
        });

        it('should handle expressions with only numbers and operators', () => {
            expect(extractVariables('1 + 2 * (3 - 4) / 5')).to.deep.equal([]);
        });

        it('should handle expressions with whitespace around variables', () => {
            expect(extractVariables('  x   +   y ')).to.deep.equal(['x', 'y'].sort());
        });

        it('should return empty for invalid syntax that mathjs cannot parse', () => {
            expect(extractVariables('2 + * 3')).to.deep.equal([]);
            expect(extractVariables('x + (y')).to.deep.equal([]);
        });
    });

    describe('isValidNumericInput()', () => {
        it('should return true for valid integer inputs', () => {
            expect(isValidNumericInput('123')).to.be.true;
            expect(isValidNumericInput('-45')).to.be.true;
            expect(isValidNumericInput('0')).to.be.true;
        });

        it('should return true for valid decimal inputs', () => {
            expect(isValidNumericInput('3.14')).to.be.true;
            expect(isValidNumericInput('-0.5')).to.be.true;
            expect(isValidNumericInput('.5')).to.be.true; // Leading decimal
            expect(isValidNumericInput('5.')).to.be.true; // Trailing decimal
        });

        it('should return true for valid scientific notation inputs', () => {
            expect(isValidNumericInput('1e5')).to.be.true;
            expect(isValidNumericInput('2.3e-2')).to.be.true;
            expect(isValidNumericInput('1.23e+4')).to.be.true;
        });

        it('should return true for string representation of zero', () => {
            expect(isValidNumericInput('0')).to.be.true;
            expect(isValidNumericInput('0.0')).to.be.true;
        });

        it('should return false for empty string or whitespace', () => {
            expect(isValidNumericInput('')).to.be.false;
            expect(isValidNumericInput('   ')).to.be.false;
        });

        it('should return false for non-numeric strings', () => {
            expect(isValidNumericInput('abc')).to.be.false;
            expect(isValidNumericInput('hello world')).to.be.false;
            expect(isValidNumericInput('123a')).to.be.false; // Mixed numeric and alpha
            expect(isValidNumericInput('NaN')).to.be.false; // String 'NaN'
        });

        it('should return false for "Infinity" or "-Infinity" as string', () => {
            expect(isValidNumericInput('Infinity')).to.be.false;
            expect(isValidNumericInput('-Infinity')).to.be.false;
        });

        it('should return false for null or undefined inputs (type system might prevent, but for robustness)', () => {
            // @ts-ignore - testing runtime behavior for potentially invalid input types
            expect(isValidNumericInput(null)).to.be.false;
            // @ts-ignore
            expect(isValidNumericInput(undefined)).to.be.false;
        });
    });
});
