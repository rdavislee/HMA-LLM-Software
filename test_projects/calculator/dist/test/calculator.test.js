"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const chai_1 = require("chai");
const calculator_1 = require("../src/calculator"); // Assuming Calculator class exists and implements ICalculator
const calculator = new calculator_1.Calculator();
const PI = Math.PI;
const E = Math.E;
const TOLERANCE = 1e-9; // For standard floating point comparisons
const LARGE_NUMBER_TOLERANCE = 1e85; // Adjusted for extremely large floating point numbers, based on observed precision loss relative to magnitude
describe('Calculator', () => {
    // Test Partitions for Basic Arithmetic:
    // - Positive numbers
    // - Negative numbers
    // - Mixed positive/negative
    // - Zero
    // - Floating point numbers
    // - Edge cases like division by zero
    describe('IBasicArithmetic', () => {
        describe('add', () => {
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
                (0, chai_1.expect)(calculator.add(7, 0)).to.equal(7);
                (0, chai_1.expect)(calculator.add(0, -7)).to.equal(-7);
            });
            it('should handle floating point numbers', () => {
                (0, chai_1.expect)(calculator.add(0.1, 0.2)).to.be.closeTo(0.3, TOLERANCE);
            });
            it('should handle large numbers', () => {
                (0, chai_1.expect)(calculator.add(1e100, 2e100)).to.be.closeTo(3e100, LARGE_NUMBER_TOLERANCE);
            });
        });
        describe('subtract', () => {
            it('should correctly subtract two positive numbers', () => {
                (0, chai_1.expect)(calculator.subtract(5, 3)).to.equal(2);
            });
            it('should correctly subtract a positive and a negative number', () => {
                (0, chai_1.expect)(calculator.subtract(5, -3)).to.equal(8);
            });
            it('should correctly subtract two negative numbers', () => {
                (0, chai_1.expect)(calculator.subtract(-2, -3)).to.equal(1);
            });
            it('should correctly subtract zero from a number', () => {
                (0, chai_1.expect)(calculator.subtract(7, 0)).to.equal(7);
                (0, chai_1.expect)(calculator.subtract(0, 7)).to.equal(-7);
            });
            it('should handle floating point numbers', () => {
                (0, chai_1.expect)(calculator.subtract(0.3, 0.1)).to.be.closeTo(0.2, TOLERANCE);
            });
        });
        describe('multiply', () => {
            it('should correctly multiply two positive numbers', () => {
                (0, chai_1.expect)(calculator.multiply(2, 3)).to.equal(6);
            });
            it('should correctly multiply a positive and a negative number', () => {
                (0, chai_1.expect)(calculator.multiply(5, -3)).to.equal(-15);
            });
            it('should correctly multiply two negative numbers', () => {
                (0, chai_1.expect)(calculator.multiply(-2, -3)).to.equal(6);
            });
            it('should correctly multiply by zero', () => {
                (0, chai_1.expect)(calculator.multiply(7, 0)).to.equal(0);
                (0, chai_1.expect)(calculator.multiply(0, -7)).to.equal(0);
            });
            it('should handle floating point numbers', () => {
                (0, chai_1.expect)(calculator.multiply(0.1, 0.2)).to.be.closeTo(0.02, TOLERANCE);
            });
        });
        describe('divide', () => {
            it('should correctly divide two positive numbers', () => {
                (0, chai_1.expect)(calculator.divide(6, 3)).to.equal(2);
            });
            it('should correctly divide a positive by a negative number', () => {
                (0, chai_1.expect)(calculator.divide(6, -3)).to.equal(-2);
            });
            it('should correctly divide two negative numbers', () => {
                (0, chai_1.expect)(calculator.divide(-6, -3)).to.equal(2);
            });
            it('should correctly divide zero by a non-zero number', () => {
                (0, chai_1.expect)(calculator.divide(0, 7)).to.equal(0);
            });
            it('should return Infinity when dividing a positive number by zero', () => {
                (0, chai_1.expect)(calculator.divide(7, 0)).to.equal(Infinity);
            });
            it('should return -Infinity when dividing a negative number by zero', () => {
                (0, chai_1.expect)(calculator.divide(-7, 0)).to.equal(-Infinity);
            });
            it('should return NaN when dividing zero by zero', () => {
                (0, chai_1.expect)(calculator.divide(0, 0)).to.be.NaN;
            });
            it('should handle floating point numbers', () => {
                (0, chai_1.expect)(calculator.divide(1, 3)).to.be.closeTo(0.3333333333333333, TOLERANCE);
            });
        });
    });
    // Test Partitions for Exponents:
    // - Positive base, positive exponent
    // - Positive base, negative exponent
    // - Negative base, even exponent
    // - Negative base, odd exponent
    // - Base 0, positive exponent
    // - Base 0, negative exponent
    // - Base 0, exponent 0
    // - Base 1, any exponent
    // - Any base, exponent 0
    // - Any base, exponent 1
    // - Fractional exponents
    // - Large numbers
    // - Floating point numbers
    describe('IExponents', () => {
        describe('power', () => {
            it('should correctly calculate positive base to positive exponent', () => {
                (0, chai_1.expect)(calculator.power(2, 3)).to.equal(8);
            });
            it('should correctly calculate positive base to negative exponent', () => {
                (0, chai_1.expect)(calculator.power(2, -1)).to.equal(0.5);
                (0, chai_1.expect)(calculator.power(2, -3)).to.equal(0.125);
            });
            it('should correctly calculate negative base to even exponent', () => {
                (0, chai_1.expect)(calculator.power(-2, 2)).to.equal(4);
            });
            it('should correctly calculate negative base to odd exponent', () => {
                (0, chai_1.expect)(calculator.power(-2, 3)).to.equal(-8);
            });
            it('should correctly calculate base 0 to positive exponent', () => {
                (0, chai_1.expect)(calculator.power(0, 5)).to.equal(0);
            });
            it('should return Infinity for base 0 to negative exponent', () => {
                (0, chai_1.expect)(calculator.power(0, -2)).to.equal(Infinity);
            });
            it('should return 1 for base 0 to exponent 0', () => {
                (0, chai_1.expect)(calculator.power(0, 0)).to.equal(1);
            });
            it('should return 1 for base 1 to any exponent', () => {
                (0, chai_1.expect)(calculator.power(1, 100)).to.equal(1);
                (0, chai_1.expect)(calculator.power(1, -5)).to.equal(1);
                (0, chai_1.expect)(calculator.power(1, 0)).to.equal(1);
            });
            it('should return 1 for any base to exponent 0', () => {
                (0, chai_1.expect)(calculator.power(10, 0)).to.equal(1);
                (0, chai_1.expect)(calculator.power(-5, 0)).to.equal(1);
                (0, chai_1.expect)(calculator.power(0.5, 0)).to.equal(1);
            });
            it('should return base for any base to exponent 1', () => {
                (0, chai_1.expect)(calculator.power(10, 1)).to.equal(10);
                (0, chai_1.expect)(calculator.power(-5, 1)).to.equal(-5);
            });
            it('should handle fractional exponents (square root)', () => {
                (0, chai_1.expect)(calculator.power(9, 0.5)).to.be.closeTo(3, TOLERANCE);
                (0, chai_1.expect)(calculator.power(4, 0.5)).to.be.closeTo(2, TOLERANCE);
            });
            it('should handle fractional exponents (cube root)', () => {
                (0, chai_1.expect)(calculator.power(8, 1 / 3)).to.be.closeTo(2, TOLERANCE);
            });
            it('should handle large exponents', () => {
                (0, chai_1.expect)(calculator.power(10, 10)).to.be.closeTo(1e10, TOLERANCE);
            });
            it('should handle floating point base and exponent', () => {
                (0, chai_1.expect)(calculator.power(2.5, 2.5)).to.be.closeTo(9.88211768802613, TOLERANCE);
            });
            it('should return NaN for negative base and fractional exponent with even denominator', () => {
                (0, chai_1.expect)(calculator.power(-4, 0.5)).to.be.NaN;
            });
        });
    });
    // Test Partitions for Logarithms:
    // - Valid positive value and base > 1
    // - Value 1
    // - Value = base
    // - Value < 0
    // - Value 0
    // - Base < 0, Base 0, Base 1
    // - Large numbers, small numbers
    // - Floating point numbers
    describe('ILogarithms', () => {
        describe('log', () => {
            it('should correctly calculate log base 10 of 100', () => {
                (0, chai_1.expect)(calculator.log(100, 10)).to.be.closeTo(2, TOLERANCE);
            });
            it('should correctly calculate log base 2 of 8', () => {
                (0, chai_1.expect)(calculator.log(8, 2)).to.be.closeTo(3, TOLERANCE);
            });
            it('should return 0 for value 1', () => {
                (0, chai_1.expect)(calculator.log(1, 10)).to.be.closeTo(0, TOLERANCE);
            });
            it('should return 1 for value equal to base', () => {
                (0, chai_1.expect)(calculator.log(5, 5)).to.be.closeTo(1, TOLERANCE);
            });
            it('should return NaN for negative value', () => {
                (0, chai_1.expect)(calculator.log(-10, 10)).to.be.NaN;
            });
            it('should return -Infinity for value 0', () => {
                (0, chai_1.expect)(calculator.log(0, 10)).to.equal(-Infinity);
            });
            it('should return NaN for base 0', () => {
                (0, chai_1.expect)(calculator.log(10, 0)).to.be.NaN;
            });
            it('should return NaN for base 1', () => {
                (0, chai_1.expect)(calculator.log(10, 1)).to.be.NaN;
            });
            it('should return NaN for negative base', () => {
                (0, chai_1.expect)(calculator.log(10, -2)).to.be.NaN;
            });
            it('should handle floating point values and bases', () => {
                (0, chai_1.expect)(calculator.log(5.5, 2.5)).to.be.closeTo(1.860488197617782, TOLERANCE);
            });
        });
        describe('ln', () => {
            it('should correctly calculate natural logarithm of E', () => {
                (0, chai_1.expect)(calculator.ln(E)).to.be.closeTo(1, TOLERANCE);
            });
            it('should correctly calculate natural logarithm of 1', () => {
                (0, chai_1.expect)(calculator.ln(1)).to.be.closeTo(0, TOLERANCE);
            });
            it('should correctly calculate natural logarithm of a positive number', () => {
                (0, chai_1.expect)(calculator.ln(10)).to.be.closeTo(2.302585092994046, TOLERANCE);
            });
            it('should return NaN for negative value', () => {
                (0, chai_1.expect)(calculator.ln(-5)).to.be.NaN;
            });
            it('should return -Infinity for value 0', () => {
                (0, chai_1.expect)(calculator.ln(0)).to.equal(-Infinity);
            });
            it('should handle floating point values', () => {
                (0, chai_1.expect)(calculator.ln(0.5)).to.be.closeTo(-0.6931471805599453, TOLERANCE);
            });
        });
    });
    // Test Partitions for Trigonometry:
    // - Common angles (0, PI/6, PI/4, PI/3, PI/2, PI, 3PI/2, 2PI)
    // - Negative angles
    // - Large angles (multiple rotations)
    // - Floating point numbers
    // - Angles where tan is undefined (testing behavior near asymptotes)
    describe('ITrigonometry', () => {
        describe('sin', () => {
            it('should return 0 for sin(0)', () => {
                (0, chai_1.expect)(calculator.sin(0)).to.be.closeTo(0, TOLERANCE);
            });
            it('should return 1 for sin(PI/2)', () => {
                (0, chai_1.expect)(calculator.sin(PI / 2)).to.be.closeTo(1, TOLERANCE);
            });
            it('should return 0 for sin(PI)', () => {
                (0, chai_1.expect)(calculator.sin(PI)).to.be.closeTo(0, TOLERANCE);
            });
            it('should return -1 for sin(3PI/2)', () => {
                (0, chai_1.expect)(calculator.sin(3 * PI / 2)).to.be.closeTo(-1, TOLERANCE);
            });
            it('should return 0 for sin(2PI)', () => {
                (0, chai_1.expect)(calculator.sin(2 * PI)).to.be.closeTo(0, TOLERANCE);
            });
            it('should handle negative angles', () => {
                (0, chai_1.expect)(calculator.sin(-PI / 2)).to.be.closeTo(-1, TOLERANCE);
            });
            it('should handle angles greater than 2PI', () => {
                (0, chai_1.expect)(calculator.sin(5 * PI / 2)).to.be.closeTo(1, TOLERANCE); // 5PI/2 = 2PI + PI/2
            });
            it('should handle common angles', () => {
                (0, chai_1.expect)(calculator.sin(PI / 6)).to.be.closeTo(0.5, TOLERANCE); // sin(30 deg)
                (0, chai_1.expect)(calculator.sin(PI / 4)).to.be.closeTo(Math.sqrt(2) / 2, TOLERANCE); // sin(45 deg)
                (0, chai_1.expect)(calculator.sin(PI / 3)).to.be.closeTo(Math.sqrt(3) / 2, TOLERANCE); // sin(60 deg)
            });
        });
        describe('cos', () => {
            it('should return 1 for cos(0)', () => {
                (0, chai_1.expect)(calculator.cos(0)).to.be.closeTo(1, TOLERANCE);
            });
            it('should return 0 for cos(PI/2)', () => {
                (0, chai_1.expect)(calculator.cos(PI / 2)).to.be.closeTo(0, TOLERANCE);
            });
            it('should return -1 for cos(PI)', () => {
                (0, chai_1.expect)(calculator.cos(PI)).to.be.closeTo(-1, TOLERANCE);
            });
            it('should return 0 for cos(3PI/2)', () => {
                (0, chai_1.expect)(calculator.cos(3 * PI / 2)).to.be.closeTo(0, TOLERANCE);
            });
            it('should return 1 for cos(2PI)', () => {
                (0, chai_1.expect)(calculator.cos(2 * PI)).to.be.closeTo(1, TOLERANCE);
            });
            it('should handle negative angles', () => {
                (0, chai_1.expect)(calculator.cos(-PI / 2)).to.be.closeTo(0, TOLERANCE);
            });
            it('should handle angles greater than 2PI', () => {
                (0, chai_1.expect)(calculator.cos(5 * PI / 2)).to.be.closeTo(0, TOLERANCE); // 5PI/2 = 2PI + PI/2
            });
            it('should handle common angles', () => {
                (0, chai_1.expect)(calculator.cos(PI / 6)).to.be.closeTo(Math.sqrt(3) / 2, TOLERANCE); // cos(30 deg)
                (0, chai_1.expect)(calculator.cos(PI / 4)).to.be.closeTo(Math.sqrt(2) / 2, TOLERANCE); // cos(45 deg)
                (0, chai_1.expect)(calculator.cos(PI / 3)).to.be.closeTo(0.5, TOLERANCE);
            });
        });
        describe('tan', () => {
            it('should return 0 for tan(0)', () => {
                (0, chai_1.expect)(calculator.tan(0)).to.be.closeTo(0, TOLERANCE);
            });
            it('should return 1 for tan(PI/4)', () => {
                (0, chai_1.expect)(calculator.tan(PI / 4)).to.be.closeTo(1, TOLERANCE);
            });
            it('should return 0 for tan(PI)', () => {
                (0, chai_1.expect)(calculator.tan(PI)).to.be.closeTo(0, TOLERANCE);
            });
            it('should handle negative angles', () => {
                (0, chai_1.expect)(calculator.tan(-PI / 4)).to.be.closeTo(-1, TOLERANCE);
            });
            it('should handle angles greater than 2PI', () => {
                (0, chai_1.expect)(calculator.tan(5 * PI / 4)).to.be.closeTo(1, TOLERANCE); // 5PI/4 = PI + PI/4
            });
            it('should handle common angles', () => {
                (0, chai_1.expect)(calculator.tan(PI / 6)).to.be.closeTo(1 / Math.sqrt(3), TOLERANCE); // tan(30 deg)
                (0, chai_1.expect)(calculator.tan(PI / 3)).to.be.closeTo(Math.sqrt(3), TOLERANCE);
            });
            it('should approach Infinity when angle is slightly less than PI/2', () => {
                (0, chai_1.expect)(calculator.tan(PI / 2 - 1e-10)).to.be.above(1e9);
            });
            it('should approach -Infinity when angle is slightly greater than PI/2', () => {
                (0, chai_1.expect)(calculator.tan(PI / 2 + 1e-10)).to.be.below(-1e10);
            });
            it('should approach Infinity when angle is slightly less than 3PI/2', () => {
                (0, chai_1.expect)(calculator.tan(3 * PI / 2 - 1e-10)).to.be.above(1e9);
            });
            it('should approach -Infinity when angle is slightly greater than 3PI/2', () => {
                (0, chai_1.expect)(calculator.tan(3 * PI / 2 + 1e-10)).to.be.below(-1e10);
            });
        });
    });
});
