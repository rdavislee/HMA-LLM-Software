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
            if (a === 0)
                return NaN; // 0/0 is NaN
            return a > 0 ? Infinity : -Infinity; // Positive/0 is Infinity, Negative/0 is -Infinity
        }
        return a / b;
    }
    power(base, exponent) {
        return Math.pow(base, exponent);
    }
    log(value, base) {
        // Math.log returns natural logarithm (base e)
        // log_b(x) = ln(x) / ln(b)
        if (value < 0 || base <= 0 || base === 1) {
            return NaN;
        }
        return Math.log(value) / Math.log(base);
    }
    ln(value) {
        return Math.log(value);
    }
    sin(angle) {
        return Math.sin(angle);
    }
    cos(angle) {
        return Math.cos(angle);
    }
    tan(angle) {
        return Math.tan(angle);
    }
}
exports.Calculator = Calculator;
