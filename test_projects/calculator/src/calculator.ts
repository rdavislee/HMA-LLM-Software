import { Calculator } from './calculator.interface';

/**
 * @class BasicCalculator
 * Implements the Calculator interface, providing concrete implementations for basic arithmetic operations.
 */
export class BasicCalculator implements Calculator {
  /**
   * Adds two numbers.
   * @param a - The first number.
   * @param b - The second number.
   * @returns The sum of a and b.
   */
  add(a: number, b: number): number {
    return a + b;
  }

  /**
   * Subtracts the second number from the first.
   * @param a - The number to subtract from.
   * @param b - The number to subtract.
   * @returns The difference between a and b.
   */
  subtract(a: number, b: number): number {
    return a - b;
  }

  /**
   * Multiplies two numbers.
   * @param a - The first number.
   * @param b - The second number.
   * @returns The product of a and b.
   */
  multiply(a: number, b: number): number {
    return a * b;
  }

  /**
   * Divides the first number by the second.
   * @param a - The dividend.
   * @param b - The divisor.
   * @returns The quotient of a divided by b. Returns Infinity, -Infinity, or NaN for division by zero,
   *          aligning with standard JavaScript behavior.
   */
  divide(a: number, b: number): number {
    // Explicitly handle division by zero to ensure it returns Infinity, -Infinity, or NaN
    // as per test expectations, and to avoid any potential environment-specific errors
    // if native division behavior is altered or strict.
    if (b === 0) {
      if (a === 0) {
        return NaN; // 0/0 is NaN
      } else if (a > 0) {
        return Infinity; // Positive number / 0 is Infinity
      } else {
        return -Infinity; // Negative number / 0 is -Infinity
      }
    }
    return a / b;
  }

  /**
   * Calculates the power of a base to an exponent.
   * @param base - The base number.
   * @param exponent - The exponent.
   * @returns The result of base raised to the power of exponent.
   */
  power(base: number, exponent: number): number {
    return Math.pow(base, exponent);
  }
}