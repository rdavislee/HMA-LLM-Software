import { Calculator } from '../src/calculator.interface';
import { BasicCalculator } from '../src/calculator'; // Assuming BasicCalculator is the implementation class

// Import expect from Chai for assertions
import { expect } from 'chai';

describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    // Initialize a new calculator instance for each test to ensure isolation
    calculator = new BasicCalculator();
  });

  describe('add', () => {
    // Partitions:
    // - Positive numbers
    // - Negative numbers
    // - Zero
    // - Mixed positive and negative
    // - Large numbers (within safe integer limits)
    // - Decimal numbers
    // - Edge cases: MAX_SAFE_INTEGER boundary

    it('should correctly add two positive numbers', () => {
      expect(calculator.add(2, 3)).to.be.equal(5);
    });

    it('should correctly add a positive and a negative number', () => {
      expect(calculator.add(5, -3)).to.be.equal(2);
      expect(calculator.add(-5, 3)).to.be.equal(-2);
    });

    it('should correctly add two negative numbers', () => {
      expect(calculator.add(-2, -3)).to.be.equal(-5);
    });

    it('should correctly add zero to a number', () => {
      expect(calculator.add(5, 0)).to.be.equal(5);
      expect(calculator.add(0, 5)).to.be.equal(5);
      expect(calculator.add(0, 0)).to.be.equal(0);
    });

    it('should handle large numbers near MAX_SAFE_INTEGER', () => {
      expect(calculator.add(Number.MAX_SAFE_INTEGER - 1, 1)).to.be.equal(Number.MAX_SAFE_INTEGER);
      expect(calculator.add(Number.MAX_SAFE_INTEGER, 0)).to.be.equal(Number.MAX_SAFE_INTEGER);
    });

    it('should handle addition that exceeds MAX_SAFE_INTEGER (potential precision loss)', () => {
      // JavaScript numbers are float64, so very large integers might lose precision.
      // The expectation is based on standard JS number behavior.
      expect(calculator.add(Number.MAX_SAFE_INTEGER, 2)).to.be.equal(9007199254740993);
    });

    it('should correctly add decimal numbers', () => {
      // Using a small delta for floating point comparisons with to.be.closeTo
      expect(calculator.add(0.1, 0.2)).to.be.closeTo(0.3, 1e-9);
      expect(calculator.add(1.23, 4.56)).to.be.closeTo(5.79, 1e-9);
      expect(calculator.add(-0.1, -0.2)).to.be.closeTo(-0.3, 1e-9);
    });
  });

  describe('subtract', () => {
    // Partitions:
    // - Positive numbers
    // - Negative numbers
    // - Zero
    // - Mixed positive and negative
    // - Subtracting from zero
    // - Subtracting zero
    // - Large numbers (within safe integer limits)
    // - Decimal numbers
    // - Edge cases: MAX_SAFE_INTEGER boundary

    it('should correctly subtract two positive numbers', () => {
      expect(calculator.subtract(5, 3)).to.be.equal(2);
    });

    it('should correctly subtract a positive from a negative number', () => {
      expect(calculator.subtract(-5, 3)).to.be.equal(-8);
    });

    it('should correctly subtract a negative from a positive number', () => {
      expect(calculator.subtract(5, -3)).to.be.equal(8);
    });

    it('should correctly subtract two negative numbers', () => {
      expect(calculator.subtract(-2, -3)).to.be.equal(1);
    });

    it('should correctly subtract zero from a number', () => {
      expect(calculator.subtract(5, 0)).to.be.equal(5);
    });

    it('should correctly subtract a number from zero', () => {
      expect(calculator.subtract(0, 5)).to.be.equal(-5);
    });

    it('should handle large numbers near MAX_SAFE_INTEGER', () => {
      expect(calculator.subtract(Number.MAX_SAFE_INTEGER, 1)).to.be.equal(Number.MAX_SAFE_INTEGER - 1);
      expect(calculator.subtract(Number.MAX_SAFE_INTEGER, 0)).to.be.equal(Number.MAX_SAFE_INTEGER);
    });

    it('should correctly subtract decimal numbers', () => {
      expect(calculator.subtract(0.3, 0.1)).to.be.closeTo(0.2, 1e-9);
      expect(calculator.subtract(4.56, 1.23)).to.be.closeTo(3.33, 1e-9);
      expect(calculator.subtract(-0.3, -0.1)).to.be.closeTo(-0.2, 1e-9);
    });
  });

  describe('multiply', () => {
    // Partitions:
    // - Positive numbers
    // - Negative numbers
    // - Zero (multiplication by zero)
    // - Mixed positive and negative
    // - One (multiplication by one)
    // - Large numbers (within safe integer limits, potential overflow)
    // - Decimal numbers
    // - Edge cases: MAX_SAFE_INTEGER boundary

    it('should correctly multiply two positive numbers', () => {
      expect(calculator.multiply(2, 3)).to.be.equal(6);
    });

    it('should correctly multiply a positive and a negative number', () => {
      expect(calculator.multiply(5, -3)).to.be.equal(-15);
      expect(calculator.multiply(-5, 3)).to.be.equal(-15);
    });

    it('should correctly multiply two negative numbers', () => {
      expect(calculator.multiply(-2, -3)).to.be.equal(6);
    });

    it('should correctly multiply by zero', () => {
      expect(calculator.multiply(5, 0)).to.be.equal(0);
      expect(calculator.multiply(0, 5)).to.be.equal(0);
      expect(calculator.multiply(0, 0)).to.be.equal(0);
      expect(calculator.multiply(-5, 0)).to.be.equal(0);
    });

    it('should correctly multiply by one', () => {
      expect(calculator.multiply(5, 1)).to.be.equal(5);
      expect(calculator.multiply(1, 5)).to.be.equal(5);
      expect(calculator.multiply(-5, 1)).to.be.equal(-5);
    });

    it('should handle large numbers that result in overflow to Infinity', () => {
      expect(calculator.multiply(Number.MAX_VALUE, 2)).to.be.equal(Infinity);
    });

    it('should handle large numbers that result in underflow to -Infinity', () => {
      expect(calculator.multiply(-Number.MAX_VALUE, 2)).to.be.equal(-Infinity);
    });

    it('should correctly multiply decimal numbers', () => {
      expect(calculator.multiply(0.1, 0.2)).to.be.closeTo(0.02, 1e-9);
      expect(calculator.multiply(1.5, 2.5)).to.be.closeTo(3.75, 1e-9);
      expect(calculator.multiply(-1.5, 2.5)).to.be.closeTo(-3.75, 1e-9);
    });
  });

  describe('divide', () => {
    // Partitions:
    // - Positive numbers
    // - Negative numbers
    // - Zero dividend
    // - Division by one
    // - Division by negative one
    // - Decimal results
    // - Edge case: Division by zero (Infinity, -Infinity, NaN)
    // - Large numbers (potential underflow/overflow)

    it('should correctly divide two positive numbers', () => {
      expect(calculator.divide(6, 3)).to.be.equal(2);
    });

    it('should correctly divide a positive by a negative number', () => {
      expect(calculator.divide(6, -3)).to.be.equal(-2);
    });

    it('should correctly divide a negative by a positive number', () => {
      expect(calculator.divide(-6, 3)).to.be.equal(-2);
    });

    it('should correctly divide two negative numbers', () => {
      expect(calculator.divide(-6, -3)).to.be.equal(2);
    });

    it('should correctly divide zero by a non-zero number', () => {
      expect(calculator.divide(0, 5)).to.be.equal(0);
      expect(calculator.divide(0, -5)).to.be.equal(0);
    });

    it('should correctly divide by one', () => {
      expect(calculator.divide(5, 1)).to.be.equal(5);
      expect(calculator.divide(-5, 1)).to.be.equal(-5);
    });

    it('should correctly divide by negative one', () => {
      expect(calculator.divide(5, -1)).to.be.equal(-5);
      expect(calculator.divide(-5, -1)).to.be.equal(5);
    });

    it('should handle division resulting in decimal numbers', () => {
      expect(calculator.divide(7, 2)).to.be.equal(3.5);
      expect(calculator.divide(1, 3)).to.be.closeTo(0.3333333333333333, 1e-9);
    });

    it('should return Infinity when dividing a positive number by zero', () => {
      expect(calculator.divide(5, 0)).to.be.equal(Infinity);
    });

    it('should return -Infinity when dividing a negative number by zero', () => {
      expect(calculator.divide(-5, 0)).to.be.equal(-Infinity);
    });

    it('should return NaN when dividing zero by zero', () => {
      expect(calculator.divide(0, 0)).to.be.NaN;
    });

    it('should handle large numbers resulting in small non-zero values', () => {
      expect(calculator.divide(1, Number.MAX_VALUE)).to.be.closeTo(0, 1e-9); // Underflow
    });
  });

  describe('power', () => {
    // Partitions:
    // - Positive integer exponent
    // - Negative integer exponent
    // - Zero exponent (base^0 = 1, except 0^0)
    // - Base is 0
    // - Base is 1
    // - Base is -1
    // - Exponent is 1
    // - Fractional exponent (e.g., 0.5 for square root)
    // - Large base/exponent (potential overflow/underflow)
    // - Negative base with fractional exponent (should be NaN)

    it('should correctly calculate positive integer powers', () => {
      expect(calculator.power(2, 3)).to.be.equal(8); // 2^3
      expect(calculator.power(5, 2)).to.be.equal(25); // 5^2
    });

    it('should correctly calculate power with base 0 and positive exponent', () => {
      expect(calculator.power(0, 5)).to.be.equal(0); // 0^5 = 0
    });

    it('should correctly calculate power with base 1', () => {
      expect(calculator.power(1, 100)).to.be.equal(1); // 1^100 = 1
    });

    it('should correctly calculate power with base -1 and even exponent', () => {
      expect(calculator.power(-1, 2)).to.be.equal(1); // (-1)^2 = 1
    });

    it('should correctly calculate power with base -1 and odd exponent', () => {
      expect(calculator.power(-1, 3)).to.be.equal(-1); // (-1)^3 = -1
    });

    it('should return 1 for any non-zero base with exponent 0', () => {
      expect(calculator.power(5, 0)).to.be.equal(1); // 5^0 = 1
      expect(calculator.power(-5, 0)).to.be.equal(1); // (-5)^0 = 1
      expect(calculator.power(0.5, 0)).to.be.equal(1); // 0.5^0 = 1
    });

    it('should return NaN for 0^0', () => {
      expect(calculator.power(0, 0)).to.be.NaN; // 0^0 is NaN in JS Math.pow
    });

    it('should correctly calculate power with exponent 1', () => {
      expect(calculator.power(7, 1)).to.be.equal(7);
    });

    it('should correctly calculate negative integer powers', () => {
      expect(calculator.power(2, -2)).to.be.equal(0.25);
      expect(calculator.power(4, -1)).to.be.equal(0.25);
    });

    it('should correctly calculate fractional powers (square roots)', () => {
      expect(calculator.power(9, 0.5)).to.be.equal(3);
      expect(calculator.power(25, 0.5)).to.be.equal(5);
    });

    it('should correctly calculate fractional powers (cube roots)', () => {
      expect(calculator.power(8, 1/3)).to.be.closeTo(2, 1e-9);
    });

    it('should handle large positive exponents resulting in Infinity', () => {
      expect(calculator.power(2, 1024)).to.be.equal(Infinity);
    });

    it('should handle large negative exponents resulting in 0', () => {
      expect(calculator.power(2, -1024)).to.be.equal(0);
    });

    it('should return NaN for negative base with fractional exponent', () => {
      expect(calculator.power(-4, 0.5)).to.be.NaN;
    });

    it('should handle negative base with negative odd exponent', () => {
      expect(calculator.power(-2, -3)).to.be.closeTo(-0.125, 1e-9);
    });

    it('should handle negative base with negative even exponent', () => {
      expect(calculator.power(-2, -2)).to.be.closeTo(0.25, 1e-9);
    });
  });
});