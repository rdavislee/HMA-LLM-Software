"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const chai_1 = require("chai");
// Corrected import path: In a TypeScript test file, you should import from the TypeScript source file (src/calculator.ts).
// The TypeScript compiler will then correctly resolve this to the compiled JavaScript file (dist/src/calculator.js) at runtime.
const calculator_1 = require("../src/calculator");
describe('Calculator', () => {
    let calculator;
    beforeEach(() => {
        calculator = new calculator_1.Calculator();
    });
    // --- Basic Arithmetic Tests ---
    describe('add', () => {
        // Partitions: positive numbers, negative numbers, mixed signs, zero, decimals, large numbers.
        it('should correctly add two positive numbers', () => {
            (0, chai_1.expect)(calculator.add(2, 3)).to.equal(5);
        });
        it('should correctly add a positive and a negative number', () => {
            (0, chai_1.expect)(calculator.add(5, -3)).to.equal(2);
        });
        it('should correctly add two negative numbers', () => {
            (0, chai_1.expect)(calculator.add(-2, -3)).to.equal(-5);
        });
        it('should correctly add zero to a number', () => {
            (0, chai_1.expect)(calculator.add(5, 0)).to.equal(5);
            (0, chai_1.expect)(calculator.add(0, 0)).to.equal(0);
        });
        it('should handle decimal numbers correctly', () => {
            (0, chai_1.expect)(calculator.add(0.1, 0.2)).to.be.closeTo(0.3, 1e-9);
        });
        it('should handle large numbers without precision loss (if supported by JS numbers)', () => {
            (0, chai_1.expect)(calculator.add(1e100, 2e100)).to.be.closeTo(3e100, 1e90); // Tolerance for large numbers
        });
    });
    describe('subtract', () => {
        // Partitions: positive numbers, negative numbers, mixed signs, zero, decimals, large numbers.
        it('should correctly subtract two positive numbers', () => {
            (0, chai_1.expect)(calculator.subtract(5, 3)).to.equal(2);
        });
        it('should correctly subtract a negative number', () => {
            (0, chai_1.expect)(calculator.subtract(5, -3)).to.equal(8);
        });
        it('should correctly subtract from a negative number', () => {
            (0, chai_1.expect)(calculator.subtract(-5, 3)).to.equal(-8);
        });
        it('should correctly subtract two negative numbers', () => {
            (0, chai_1.expect)(calculator.subtract(-2, -3)).to.equal(1);
        });
        it('should correctly subtract zero from a number', () => {
            (0, chai_1.expect)(calculator.subtract(5, 0)).to.equal(5);
            (0, chai_1.expect)(calculator.subtract(0, 0)).to.equal(0);
        });
        it('should handle decimal numbers correctly', () => {
            (0, chai_1.expect)(calculator.subtract(0.3, 0.1)).to.be.closeTo(0.2, 1e-9);
        });
        it('should handle large numbers', () => {
            (0, chai_1.expect)(calculator.subtract(3e100, 1e100)).to.be.closeTo(2e100, 1e90);
        });
    });
    describe('multiply', () => {
        // Partitions: positive numbers, negative numbers, mixed signs, zero, one, decimals, large numbers.
        it('should correctly multiply two positive numbers', () => {
            (0, chai_1.expect)(calculator.multiply(2, 3)).to.equal(6);
        });
        it('should correctly multiply by a negative number', () => {
            (0, chai_1.expect)(calculator.multiply(5, -3)).to.equal(-15);
        });
        it('should correctly multiply two negative numbers', () => {
            (0, chai_1.expect)(calculator.multiply(-2, -3)).to.equal(6);
        });
        it('should correctly multiply by zero', () => {
            (0, chai_1.expect)(calculator.multiply(5, 0)).to.equal(0);
            (0, chai_1.expect)(calculator.multiply(0, 0)).to.equal(0);
        });
        it('should correctly multiply by one', () => {
            (0, chai_1.expect)(calculator.multiply(5, 1)).to.equal(5);
        });
        it('should handle decimal numbers correctly', () => {
            (0, chai_1.expect)(calculator.multiply(0.1, 0.2)).to.be.closeTo(0.02, 1e-9);
        });
        it('should handle large numbers', () => {
            (0, chai_1.expect)(calculator.multiply(1e50, 2e50)).to.be.closeTo(2e100, 1e90);
        });
    });
    describe('divide', () => {
        // Partitions: positive numbers, negative numbers, mixed signs, zero numerator, zero denominator (Infinity, -Infinity, NaN), decimals, large numbers.
        it('should correctly divide two positive numbers', () => {
            (0, chai_1.expect)(calculator.divide(6, 3)).to.equal(2);
        });
        it('should correctly divide by a negative number', () => {
            (0, chai_1.expect)(calculator.divide(6, -3)).to.equal(-2);
        });
        it('should correctly divide two negative numbers', () => {
            (0, chai_1.expect)(calculator.divide(-6, -3)).to.equal(2);
        });
        it('should return Infinity when dividing a positive number by zero', () => {
            (0, chai_1.expect)(calculator.divide(5, 0)).to.equal(Infinity);
        });
        it('should return -Infinity when dividing a negative number by zero', () => {
            (0, chai_1.expect)(calculator.divide(-5, 0)).to.equal(-Infinity);
        });
        it('should return NaN when dividing zero by zero', () => {
            (0, chai_1.expect)(calculator.divide(0, 0)).to.be.NaN;
        });
        it('should handle decimal numbers correctly', () => {
            (0, chai_1.expect)(calculator.divide(0.3, 0.1)).to.be.closeTo(3, 1e-9);
        });
        it('should handle division resulting in a decimal', () => {
            (0, chai_1.expect)(calculator.divide(1, 3)).to.be.closeTo(0.3333333333333333, 1e-9);
        });
        it('should handle large numbers', () => {
            (0, chai_1.expect)(calculator.divide(6e100, 3e50)).to.be.closeTo(2e50, 1e40);
        });
    });
    // --- Exponents Tests ---
    describe('power', () => {
        // Partitions: positive base, negative base, zero base, positive exponent, negative exponent, zero exponent, fractional exponent, NaN results.
        it('should correctly calculate positive integer powers', () => {
            (0, chai_1.expect)(calculator.power(2, 3)).to.equal(8);
            (0, chai_1.expect)(calculator.power(5, 2)).to.equal(25);
        });
        it('should correctly calculate power with zero exponent', () => {
            (0, chai_1.expect)(calculator.power(5, 0)).to.equal(1);
            (0, chai_1.expect)(calculator.power(-5, 0)).to.equal(1);
            (0, chai_1.expect)(calculator.power(0, 0)).to.equal(1); // Math.pow(0,0) is 1 in JS
        });
        it('should correctly calculate power with exponent of one', () => {
            (0, chai_1.expect)(calculator.power(5, 1)).to.equal(5);
        });
        it('should correctly calculate power with negative exponent', () => {
            (0, chai_1.expect)(calculator.power(2, -2)).to.equal(0.25);
            (0, chai_1.expect)(calculator.power(4, -0.5)).to.equal(0.5);
        });
        it('should correctly calculate power with negative base and even exponent', () => {
            (0, chai_1.expect)(calculator.power(-2, 2)).to.equal(4);
        });
        it('should correctly calculate power with negative base and odd exponent', () => {
            (0, chai_1.expect)(calculator.power(-2, 3)).to.equal(-8);
        });
        it('should handle fractional exponents (square root)', () => {
            (0, chai_1.expect)(calculator.power(9, 0.5)).to.equal(3);
        });
        it('should handle fractional exponents (cube root)', () => {
            (0, chai_1.expect)(calculator.power(8, 1 / 3)).to.be.closeTo(2, 1e-9);
        });
        it('should return NaN for negative base and non-integer fractional exponent', () => {
            (0, chai_1.expect)(calculator.power(-4, 0.5)).to.be.NaN;
        });
        it('should handle zero base and positive exponent', () => {
            (0, chai_1.expect)(calculator.power(0, 5)).to.equal(0);
        });
        it('should handle zero base and negative exponent', () => {
            (0, chai_1.expect)(calculator.power(0, -2)).to.equal(Infinity);
        });
    });
    // --- Logarithm Tests ---
    describe('log and naturalLog', () => {
        // Partitions: positive numbers, 1, zero, negative numbers, decimals.
        it('should correctly calculate log base 10 for positive numbers', () => {
            (0, chai_1.expect)(calculator.log(100, 10)).to.be.closeTo(2, 1e-9);
            (0, chai_1.expect)(calculator.log(1000, 10)).to.be.closeTo(3, 1e-9);
            (0, chai_1.expect)(calculator.log(10, 10)).to.be.closeTo(1, 1e-9);
        });
        it('should return NaN for log of zero', () => {
            (0, chai_1.expect)(calculator.log(0, 10)).to.be.NaN;
        });
        it('should return NaN for log of a negative number', () => {
            (0, chai_1.expect)(calculator.log(-10, 10)).to.be.NaN;
            (0, chai_1.expect)(calculator.log(-0.5, 10)).to.be.NaN;
        });
        it('should return 0 for log of 1', () => {
            (0, chai_1.expect)(calculator.log(1, 10)).to.equal(0);
        });
        it('should correctly calculate natural logarithm (naturalLog) for positive numbers', () => {
            (0, chai_1.expect)(calculator.naturalLog(Math.E)).to.be.closeTo(1, 1e-9);
            (0, chai_1.expect)(calculator.naturalLog(Math.E * Math.E)).to.be.closeTo(2, 1e-9);
        });
        it('should return NaN for naturalLog of zero', () => {
            (0, chai_1.expect)(calculator.naturalLog(0)).to.be.NaN;
        });
        it('should return NaN for naturalLog of a negative number', () => {
            (0, chai_1.expect)(calculator.naturalLog(-10)).to.be.NaN;
            (0, chai_1.expect)(calculator.naturalLog(-0.5)).to.be.NaN;
        });
        it('should return 0 for naturalLog of 1', () => {
            (0, chai_1.expect)(calculator.naturalLog(1)).to.equal(0);
        });
        it('should handle decimal numbers for log', () => {
            (0, chai_1.expect)(calculator.log(Math.pow(10, 0.5), 10)).to.be.closeTo(0.5, 1e-9);
        });
        it('should handle decimal numbers for naturalLog', () => {
            (0, chai_1.expect)(calculator.naturalLog(Math.exp(0.5))).to.be.closeTo(0.5, 1e-9);
        });
        it('should return NaN for log with base 1', () => {
            (0, chai_1.expect)(calculator.log(10, 1)).to.be.NaN;
        });
        it('should return NaN for log with negative base', () => {
            (0, chai_1.expect)(calculator.log(10, -2)).to.be.NaN;
        });
    });
    // --- Trigonometry Tests ---
    describe('Trigonometry (sin, cos, tan)', () => {
        // Partitions: common angles (0, PI/2, PI, 3PI/2, 2PI), negative angles, angles > 2PI, decimals, tangent asymptotes.
        it('should correctly calculate sine for common angles', () => {
            (0, chai_1.expect)(calculator.sin(0)).to.be.closeTo(0, 1e-9);
            (0, chai_1.expect)(calculator.sin(Math.PI / 2)).to.be.closeTo(1, 1e-9);
            (0, chai_1.expect)(calculator.sin(Math.PI)).to.be.closeTo(0, 1e-9);
            (0, chai_1.expect)(calculator.sin(3 * Math.PI / 2)).to.be.closeTo(-1, 1e-9);
            (0, chai_1.expect)(calculator.sin(2 * Math.PI)).to.be.closeTo(0, 1e-9);
        });
        it('should correctly calculate cosine for common angles', () => {
            (0, chai_1.expect)(calculator.cos(0)).to.be.closeTo(1, 1e-9);
            (0, chai_1.expect)(calculator.cos(Math.PI / 2)).to.be.closeTo(0, 1e-9);
            (0, chai_1.expect)(calculator.cos(Math.PI)).to.be.closeTo(-1, 1e-9);
            (0, chai_1.expect)(calculator.cos(3 * Math.PI / 2)).to.be.closeTo(0, 1e-9);
            (0, chai_1.expect)(calculator.cos(2 * Math.PI)).to.be.closeTo(1, 1e-9);
        });
        it('should correctly calculate tangent for common angles', () => {
            (0, chai_1.expect)(calculator.tan(0)).to.be.closeTo(0, 1e-9);
            (0, chai_1.expect)(calculator.tan(Math.PI / 4)).to.be.closeTo(1, 1e-9);
            (0, chai_1.expect)(calculator.tan(3 * Math.PI / 4)).to.be.closeTo(-1, 1e-9);
            (0, chai_1.expect)(calculator.tan(Math.PI)).to.be.closeTo(0, 1e-9);
        });
        it('should handle tangent approaching PI/2 (positive infinity)', () => {
            // Test values very close to PI/2, where tan approaches positive infinity
            (0, chai_1.expect)(calculator.tan(Math.PI / 2 - 1e-12)).to.be.greaterThan(1e10);
        });
        it('should handle tangent approaching PI/2 (negative infinity)', () => {
            // Test values very close to PI/2 from the other side, where tan approaches negative infinity
            (0, chai_1.expect)(calculator.tan(Math.PI / 2 + 1e-12)).to.be.lessThan(-1e10);
        });
        it('should handle tangent at exact PI/2 (NaN or Infinity depending on implementation)', () => {
            // Depending on how the implementation handles sin/cos at PI/2, it might be Infinity or NaN. 
            // Common JS Math.tan(Math.PI/2) is a very large number, not strictly Infinity. 
            // If the implementation is sin(x)/cos(x) and cos(x) is exactly 0, it should be Infinity/NaN.
            // We'll expect a very large number or Infinity/NaN.
            const result = calculator.tan(Math.PI / 2);
            (0, chai_1.expect)(result === Infinity || result === -Infinity || isNaN(result) || Math.abs(result) > 1e15).to.be.true;
        });
        it('should handle negative angles for sin', () => {
            (0, chai_1.expect)(calculator.sin(-Math.PI / 2)).to.be.closeTo(-1, 1e-9);
            (0, chai_1.expect)(calculator.sin(-Math.PI)).to.be.closeTo(0, 1e-9);
        });
        it('should handle negative angles for cos', () => {
            (0, chai_1.expect)(calculator.cos(-Math.PI / 2)).to.be.closeTo(0, 1e-9);
            (0, chai_1.expect)(calculator.cos(-Math.PI)).to.be.closeTo(-1, 1e-9);
        });
        it('should handle negative angles for tan', () => {
            (0, chai_1.expect)(calculator.tan(-Math.PI / 4)).to.be.closeTo(-1, 1e-9);
            (0, chai_1.expect)(calculator.tan(-Math.PI)).to.be.closeTo(0, 1e-9);
        });
        it('should handle angles greater than 2PI for sin', () => {
            (0, chai_1.expect)(calculator.sin(2 * Math.PI + Math.PI / 2)).to.be.closeTo(1, 1e-9);
        });
        it('should handle angles greater than 2PI for cos', () => {
            (0, chai_1.expect)(calculator.cos(2 * Math.PI + Math.PI)).to.be.closeTo(-1, 1e-9);
        });
        it('should handle angles greater than 2PI for tan', () => {
            (0, chai_1.expect)(calculator.tan(2 * Math.PI + Math.PI / 4)).to.be.closeTo(1, 1e-9);
        });
    });
});
