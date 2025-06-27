import { ICalculator } from './calculatorInterface';

export class Calculator implements ICalculator {
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
      // Handle division by zero based on IEEE 754 standard
      // Positive infinity for positive dividend, negative infinity for negative dividend, NaN for 0/0
      return a > 0 ? Infinity : a < 0 ? -Infinity : NaN;
    }
    return a / b;
  }

  power(base: number, exponent: number): number {
    return Math.pow(base, exponent);
  }

  log(num: number, base: number): number {
    if (num <= 0 || base <= 0 || base === 1) {
      // Logarithm is undefined for non-positive numbers or base 1
      return NaN;
    }
    return Math.log(num) / Math.log(base);
  }

  naturalLog(num: number): number {
    if (num <= 0) {
      // Natural logarithm is undefined for non-positive numbers
      return NaN;
    }
    return Math.log(num);
  }

  sin(angleInRadians: number): number {
    return Math.sin(angleInRadians);
  }

  cos(angleInRadians: number): number {
    return Math.cos(angleInRadians);
  }

  tan(angleInRadians: number): number {
    return Math.tan(angleInRadians);
  }

  degreesToRadians(degrees: number): number {
    return degrees * (Math.PI / 180);
  }

  radiansToDegrees(radians: number): number {
    return radians * (180 / Math.PI);
  }
}