"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Calculator = void 0;
class Calculator {
    add(a, b) {
        return a + b;
    }
    subtract(a, b) {
        return a - b;
    }
    multiply(a, b) {
        return a * b;
    }
    divide(a, b) {
        if (b === 0) {
            // Handle division by zero based on IEEE 754 standard
            // Positive infinity for positive dividend, negative infinity for negative dividend, NaN for 0/0
            return a > 0 ? Infinity : a < 0 ? -Infinity : NaN;
        }
        return a / b;
    }
    power(base, exponent) {
        return Math.pow(base, exponent);
    }
    log(num, base) {
        if (num <= 0 || base <= 0 || base === 1) {
            // Logarithm is undefined for non-positive numbers or base 1
            return NaN;
        }
        return Math.log(num) / Math.log(base);
    }
    naturalLog(num) {
        if (num <= 0) {
            // Natural logarithm is undefined for non-positive numbers
            return NaN;
        }
        return Math.log(num);
    }
    sin(angleInRadians) {
        return Math.sin(angleInRadians);
    }
    cos(angleInRadians) {
        return Math.cos(angleInRadians);
    }
    tan(angleInRadians) {
        return Math.tan(angleInRadians);
    }
    degreesToRadians(degrees) {
        return degrees * (Math.PI / 180);
    }
    radiansToDegrees(radians) {
        return radians * (180 / Math.PI);
    }
}
exports.Calculator = Calculator;
