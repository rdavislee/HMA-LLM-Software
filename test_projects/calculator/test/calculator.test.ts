import { expect } from 'chai';
import { Calculator } from '../src/calculator.interface';

/**
 * @class DummyCalculator
 * @implements {Calculator}
 * @description A dummy implementation of the Calculator interface for testing purposes.
 *              It mimics the behavior of a real calculator, including error conditions
 *              as specified in the interface preconditions.
 */
class DummyCalculator implements Calculator {
  add(a: number, b: number): number {
    return a + b;
  }

  subtract(a: number, b: number): number {
    return a - b;
  }

  multiply(a: number, b: number): number {
    return a * b;
  }

  divide(a: number, b: number): number {
    if (b === 0) {
      // As per spec: "Throws an error or returns Infinity/NaN if b is zero."
      // JavaScript's default division by zero returns Infinity or NaN, which we'll mimic.
      if (a === 0) return NaN;
      return a > 0 ? Infinity : -Infinity;
    }
    return a / b;
  }

  power(base: number, exponent: number): number {
    return Math.pow(base, exponent);
  }

  log(base: number, value: number): number {
    if (base <= 0 || base === 1 || value <= 0) {
      // As per spec: "precondition base > 0 and base !== 1. value > 0."
      // JavaScript's Math.log behavior for invalid inputs is NaN.
      return NaN; // Or throw new Error('Invalid base or value for log');
    }
    return Math.log(value) / Math.log(base);
  }

  ln(value: number): number {
    if (value <= 0) {
      // As per spec: "precondition value > 0."
      return NaN; // Or throw new Error('Value must be positive for natural logarithm');
    }
    return Math.log(value);
  }

  sin(angle: number): number {
    return Math.sin(angle);
  }

  cos(angle: number): number {
    return Math.cos(angle);
  }

  tan(angle: number): number {
    // Check for angles where tan is undefined (odd multiples of PI/2)
    // Use a small epsilon to account for floating point inaccuracies
    const halfPi = Math.PI / 2;
    const remainder = Math.abs(angle % Math.PI);
    if (Math.abs(remainder - halfPi) < 1e-9) {
      return angle > 0 ? Infinity : -Infinity;
    }
    return Math.tan(angle);
  }

  degreesToRadians(degrees: number): number {
    return degrees * (Math.PI / 180);
  }

  radiansToDegrees(radians: number): number {
    return radians * (180 / Math.PI);
  }
}

describe('Calculator Interface Tests', () => {
  let calculator: Calculator;
  const EPSILON = 1e-9; // For floating point comparisons

  beforeEach(() => {
    calculator = new DummyCalculator();
  });

  describe('Basic Arithmetic Operations', () => {
    // Partitions for add:
    // - Positive numbers
    // - Negative numbers
    // - Mixed positive and negative
    // - Zero
    // - Large numbers
    it('should correctly add two positive numbers', () => {
      expect(calculator.add(5, 3)).to.equal(8);
    });

    it('should correctly add two negative numbers', () => {
      expect(calculator.add(-5, -3)).to.equal(-8);
    });

    it('should correctly add a positive and a negative number', () => {
      expect(calculator.add(5, -3)).to.equal(2);
      expect(calculator.add(-5, 3)).to.equal(-2);
    });

    it('should correctly add with zero', () => {
      expect(calculator.add(5, 0)).to.equal(5);
      expect(calculator.add(0, -3)).to.equal(-3);
      expect(calculator.add(0, 0)).to.equal(0);
    });

    it('should handle large numbers in addition', () => {
      expect(calculator.add(1e15, 1e15)).to.equal(2e15);
    });

    // Partitions for subtract:
    // - Positive numbers
    // - Negative numbers
    // - Mixed positive and negative
    // - Zero
    // - Large numbers
    it('should correctly subtract two positive numbers', () => {
      expect(calculator.subtract(5, 3)).to.equal(2);
    });

    it('should correctly subtract a larger positive from a smaller positive', () => {
      expect(calculator.subtract(3, 5)).to.equal(-2);
    });

    it('should correctly subtract two negative numbers', () => {
      expect(calculator.subtract(-5, -3)).to.equal(-2);
    });

    it('should correctly subtract a negative from a positive', () => {
      expect(calculator.subtract(5, -3)).to.equal(8);
    });

    it('should correctly subtract a positive from a negative', () => {
      expect(calculator.subtract(-5, 3)).to.equal(-8);
    });

    it('should correctly subtract with zero', () => {
      expect(calculator.subtract(5, 0)).to.equal(5);
      expect(calculator.subtract(0, 3)).to.equal(-3);
      expect(calculator.subtract(0, 0)).to.equal(0);
    });

    it('should handle large numbers in subtraction', () => {
      expect(calculator.subtract(2e15, 1e15)).to.equal(1e15);
    });

    // Partitions for multiply:
    // - Positive numbers
    // - Negative numbers
    // - Mixed positive and negative
    // - Zero
    // - Large numbers
    // - Fractional numbers
    it('should correctly multiply two positive numbers', () => {
      expect(calculator.multiply(5, 3)).to.equal(15);
    });

    it('should correctly multiply two negative numbers', () => {
      expect(calculator.multiply(-5, -3)).to.equal(15);
    });

    it('should correctly multiply a positive and a negative number', () => {
      expect(calculator.multiply(5, -3)).to.equal(-15);
      expect(calculator.multiply(-5, 3)).to.equal(-15);
    });

    it('should correctly multiply by zero', () => {
      expect(calculator.multiply(5, 0)).to.equal(0);
      expect(calculator.multiply(0, -3)).to.equal(0);
      expect(calculator.multiply(0, 0)).to.equal(0);
    });

    it('should handle large numbers in multiplication', () => {
      expect(calculator.multiply(1e10, 1e10)).to.equal(1e20);
    });

    it('should handle fractional numbers in multiplication', () => {
      expect(calculator.multiply(0.5, 0.2)).to.be.closeTo(0.1, EPSILON);
    });

    // Partitions for divide:
    // - Positive numbers
    // - Negative numbers
    // - Mixed positive and negative
    // - Division by zero (positive, negative, zero dividend)
    // - Division of zero by non-zero
    // - Large numbers
    // - Fractional numbers
    it('should correctly divide two positive numbers', () => {
      expect(calculator.divide(10, 2)).to.equal(5);
    });

    it('should correctly divide two negative numbers', () => {
      expect(calculator.divide(-10, -2)).to.equal(5);
    });

    it('should correctly divide a positive by a negative', () => {
      expect(calculator.divide(10, -2)).to.equal(-5);
    });

    it('should correctly divide a negative by a positive', () => {
      expect(calculator.divide(-10, 2)).to.equal(-5);
    });

    it('should return Infinity when dividing a positive number by zero', () => {
      expect(calculator.divide(10, 0)).to.equal(Infinity);
    });

    it('should return -Infinity when dividing a negative number by zero', () => {
      expect(calculator.divide(-10, 0)).to.equal(-Infinity);
    });

    it('should return NaN when dividing zero by zero', () => {
      expect(calculator.divide(0, 0)).to.be.NaN;
    });

    it('should return 0 when dividing zero by a non-zero number', () => {
      expect(calculator.divide(0, 5)).to.equal(0);
      expect(calculator.divide(0, -5)).to.equal(0);
    });

    it('should handle large numbers in division', () => {
      expect(calculator.divide(1e20, 1e10)).to.equal(1e10);
    });

    it('should handle fractional numbers in division', () => {
      expect(calculator.divide(0.75, 0.25)).to.be.closeTo(3, EPSILON);
    });
  });

  describe('Exponent Operations', () => {
    // Partitions for power:
    // - Positive base, positive exponent
    // - Positive base, negative exponent
    // - Positive base, zero exponent
    // - Positive base, exponent of 1
    // - Negative base, integer exponent (even/odd)
    // - Negative base, fractional exponent (should be NaN for real numbers)
    // - Base of 0, positive exponent
    // - Base of 0, negative exponent (Infinity)
    // - Base of 0, exponent of 0 (1)
    // - Base of 1
    // - Fractional base
    it('should calculate positive base and positive integer exponent', () => {
      expect(calculator.power(2, 3)).to.equal(8);
    });

    it('should calculate positive base and negative integer exponent', () => {
      expect(calculator.power(2, -3)).to.be.closeTo(0.125, EPSILON);
    });

    it('should calculate positive base and zero exponent (result 1)', () => {
      expect(calculator.power(5, 0)).to.equal(1);
    });

    it('should calculate positive base and exponent of 1 (result base)', () => {
      expect(calculator.power(7, 1)).to.equal(7);
    });

    it('should calculate negative base and even integer exponent', () => {
      expect(calculator.power(-2, 2)).to.equal(4);
    });

    it('should calculate negative base and odd integer exponent', () => {
      expect(calculator.power(-2, 3)).to.equal(-8);
    });

    it('should return NaN for negative base and fractional exponent', () => {
      expect(calculator.power(-2, 0.5)).to.be.NaN;
    });

    it('should return 0 for base 0 and positive exponent', () => {
      expect(calculator.power(0, 5)).to.equal(0);
    });

    it('should return Infinity for base 0 and negative exponent', () => {
      expect(calculator.power(0, -5)).to.equal(Infinity);
    });

    it('should return 1 for base 0 and exponent 0', () => {
      expect(calculator.power(0, 0)).to.equal(1); // Standard Math.pow(0,0) behavior
    });

    it('should return 1 for base 1 and any exponent', () => {
      expect(calculator.power(1, 100)).to.equal(1);
      expect(calculator.power(1, -100)).to.equal(1);
      expect(calculator.power(1, 0.5)).to.equal(1);
    });

    it('should handle fractional base and positive exponent', () => {
      expect(calculator.power(0.5, 2)).to.be.closeTo(0.25, EPSILON);
    });

    it('should handle fractional base and fractional exponent', () => {
      expect(calculator.power(9, 0.5)).to.be.closeTo(3, EPSILON);
    });
  });

  describe('Logarithm Operations', () => {
    // Partitions for log:
    // - Valid base and value
    // - Value of 1 (result 0)
    // - Value equal to base (result 1)
    // - Invalid value (non-positive)
    // - Invalid base (<=0 or 1)
    it('should calculate logarithm with a valid base and value', () => {
      expect(calculator.log(10, 100)).to.be.closeTo(2, EPSILON);
      expect(calculator.log(2, 8)).to.be.closeTo(3, EPSILON);
    });

    it('should return 0 when value is 1', () => {
      expect(calculator.log(10, 1)).to.equal(0);
      expect(calculator.log(2, 1)).to.equal(0);
    });

    it('should return 1 when value equals base', () => {
      expect(calculator.log(7, 7)).to.equal(1);
    });

    it('should return NaN for non-positive value', () => {
      expect(calculator.log(10, 0)).to.be.NaN;
      expect(calculator.log(10, -5)).to.be.NaN;
    });

    it('should return NaN for base 0', () => {
      expect(calculator.log(0, 10)).to.be.NaN;
    });

    it('should return NaN for base 1', () => {
      expect(calculator.log(1, 10)).to.be.NaN;
    });

    it('should return NaN for negative base', () => {
      expect(calculator.log(-2, 8)).to.be.NaN;
    });

    // Partitions for ln:
    // - Valid positive value
    // - Value of 1 (result 0)
    // - Invalid value (non-positive)
    it('should calculate natural logarithm for a positive value', () => {
      expect(calculator.ln(Math.E)).to.be.closeTo(1, EPSILON);
      expect(calculator.ln(10)).to.be.closeTo(2.302585092994046, EPSILON);
    });

    it('should return 0 for ln of 1', () => {
      expect(calculator.ln(1)).to.equal(0);
    });

    it('should return NaN for ln of 0', () => {
      expect(calculator.ln(0)).to.be.NaN;
    });

    it('should return NaN for ln of a negative number', () => {
      expect(calculator.ln(-5)).to.be.NaN;
    });
  });

  describe('Trigonometry Operations', () => {
    // Partitions for sin:
    // - Standard angles (0, PI/6, PI/4, PI/3, PI/2, PI, 3PI/2, 2PI)
    // - Negative angles
    // - Large angles (multiple rotations)
    it('should calculate sine for standard angles', () => {
      expect(calculator.sin(0)).to.be.closeTo(0, EPSILON);
      expect(calculator.sin(Math.PI / 6)).to.be.closeTo(0.5, EPSILON);
      expect(calculator.sin(Math.PI / 2)).to.be.closeTo(1, EPSILON);
      expect(calculator.sin(Math.PI)).to.be.closeTo(0, EPSILON);
      expect(calculator.sin((3 * Math.PI) / 2)).to.be.closeTo(-1, EPSILON);
      expect(calculator.sin(2 * Math.PI)).to.be.closeTo(0, EPSILON);
    });

    it('should calculate sine for negative angles', () => {
      expect(calculator.sin(-Math.PI / 2)).to.be.closeTo(-1, EPSILON);
    });

    it('should calculate sine for angles beyond 2PI', () => {
      expect(calculator.sin(5 * Math.PI / 2)).to.be.closeTo(1, EPSILON); // 2PI + PI/2
    });

    // Partitions for cos:
    // - Standard angles (0, PI/6, PI/4, PI/3, PI/2, PI, 3PI/2, 2PI)
    // - Negative angles
    // - Large angles (multiple rotations)
    it('should calculate cosine for standard angles', () => {
      expect(calculator.cos(0)).to.be.closeTo(1, EPSILON);
      expect(calculator.cos(Math.PI / 6)).to.be.closeTo(Math.sqrt(3) / 2, EPSILON);
      expect(calculator.cos(Math.PI / 2)).to.be.closeTo(0, EPSILON);
      expect(calculator.cos(Math.PI)).to.be.closeTo(-1, EPSILON);
      expect(calculator.cos((3 * Math.PI) / 2)).to.be.closeTo(0, EPSILON);
      expect(calculator.cos(2 * Math.PI)).to.be.closeTo(1, EPSILON);
    });

    it('should calculate cosine for negative angles', () => {
      expect(calculator.cos(-Math.PI)).to.be.closeTo(-1, EPSILON);
    });

    it('should calculate cosine for angles beyond 2PI', () => {
      expect(calculator.cos(3 * Math.PI)).to.be.closeTo(-1, EPSILON); // 2PI + PI
    });

    // Partitions for tan:
    // - Standard angles (0, PI/4, PI, etc.)
    // - Angles where tan is undefined (PI/2, 3PI/2, etc.)
    // - Negative angles
    it('should calculate tangent for standard angles', () => {
      expect(calculator.tan(0)).to.be.closeTo(0, EPSILON);
      expect(calculator.tan(Math.PI / 4)).to.be.closeTo(1, EPSILON);
      expect(calculator.tan(Math.PI)).to.be.closeTo(0, EPSILON);
    });

    it('should return Infinity for tan of PI/2 (90 degrees)', () => {
      expect(calculator.tan(Math.PI / 2)).to.equal(Infinity);
    });

    it('should return -Infinity for tan of -PI/2 (-90 degrees)', () => {
      expect(calculator.tan(-Math.PI / 2)).to.equal(-Infinity);
    });

    it('should return Infinity for tan of 3PI/2 (270 degrees)', () => {
      expect(calculator.tan(3 * Math.PI / 2)).to.equal(Infinity);
    });

    it('should calculate tangent for negative angles', () => {
      expect(calculator.tan(-Math.PI / 4)).to.be.closeTo(-1, EPSILON);
    });

    // Partitions for degreesToRadians:
    // - Standard angles (0, 30, 45, 60, 90, 180, 360)
    // - Negative angles
    it('should convert degrees to radians correctly for standard angles', () => {
      expect(calculator.degreesToRadians(0)).to.be.closeTo(0, EPSILON);
      expect(calculator.degreesToRadians(90)).to.be.closeTo(Math.PI / 2, EPSILON);
      expect(calculator.degreesToRadians(180)).to.be.closeTo(Math.PI, EPSILON);
      expect(calculator.degreesToRadians(360)).to.be.closeTo(2 * Math.PI, EPSILON);
      expect(calculator.degreesToRadians(45)).to.be.closeTo(Math.PI / 4, EPSILON);
    });

    it('should convert negative degrees to radians correctly', () => {
      expect(calculator.degreesToRadians(-90)).to.be.closeTo(-Math.PI / 2, EPSILON);
    });

    // Partitions for radiansToDegrees:
    // - Standard radians (0, PI/2, PI, 2PI)
    // - Negative radians
    it('should convert radians to degrees correctly for standard radians', () => {
      expect(calculator.radiansToDegrees(0)).to.be.closeTo(0, EPSILON);
      expect(calculator.radiansToDegrees(Math.PI / 2)).to.be.closeTo(90, EPSILON);
      expect(calculator.radiansToDegrees(Math.PI)).to.be.closeTo(180, EPSILON);
      expect(calculator.radiansToDegrees(2 * Math.PI)).to.be.closeTo(360, EPSILON);
      expect(calculator.radiansToDegrees(Math.PI / 4)).to.be.closeTo(45, EPSILON);
    });

    it('should convert negative radians to degrees correctly', () => {
      expect(calculator.radiansToDegrees(-Math.PI / 2)).to.be.closeTo(-90, EPSILON);
    });
  });
});
