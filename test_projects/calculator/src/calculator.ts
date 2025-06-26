import { Calculator } from './calculator.interface';

/**
 * @class CalculatorImpl
 * @implements Calculator
 * @description Implements the Calculator interface, providing methods for basic arithmetic,
 *              exponents, logarithms, and trigonometry. Handles common edge cases.
 */
class CalculatorImpl implements Calculator {
  /**
   * Adds two numbers.
   * @param {number} a The first number.
   * @param {number} b The second number.
   * @returns {number} The sum of a and b.
   */
  add(a: number, b: number): number {
    return a + b;
  }

  /**
   * Subtracts the second number from the first.
   * @param {number} a The first number (minuend).
   * @param {number} b The second number (subtrahend).
   * @returns {number} The difference of a and b.
   */
  subtract(a: number, b: number): number {
    return a - b;
  }

  /**
   * Multiplies two numbers.
   * @param {number} a The first number.
   * @param {number} b The second number.
   * @returns {number} The product of a and b.
   */
  multiply(a: number, b: number): number {
    return a * b;
  }

  /**
   * Divides the first number by the second.
   * Handles division by zero by returning Infinity, -Infinity, or NaN as per JavaScript's native division behavior.
   * @param {number} a The dividend.
   * @param {number} b The divisor.
   * @returns {number} The quotient of a divided by b.
   */
  divide(a: number, b: number): number {
    // JavaScript's native division handles division by zero by returning Infinity, -Infinity, or NaN.
    // This aligns with the postcondition "Throws an error or returns Infinity/NaN if b is zero."
    return a / b;
  }

  /**
   * Calculates the result of a base raised to an exponent.
   * @param {number} base The base number.
   * @param {number} exponent The exponent.
   * @returns {number} The result of base^exponent.
   */
  power(base: number, exponent: number): number {
    return Math.pow(base, exponent);
  }

  /**
   * Calculates the logarithm of a value to a specified base.
   * Handles edge cases where base <= 0, base === 1, or value <= 0 by returning NaN or Infinity as appropriate.
   * @param {number} base The base of the logarithm.
   * @param {number} value The value for which to calculate the logarithm.
   * @returns {number} The logarithm of value to the given base.
   */
  log(base: number, value: number): number {
    // Math.log returns NaN for non-positive values.
    // If base is 1, Math.log(base) is 0, leading to division by zero, resulting in Infinity or NaN.
    // If base is non-positive, Math.log(base) is NaN.
    // These behaviors align with the mathematical definition and common numerical libraries.
    return Math.log(value) / Math.log(base);
  }

  /**
   * Calculates the natural logarithm (base e) of a value.
   * Handles edge cases where value <= 0 by returning NaN.
   * @param {number} value The value for which to calculate the natural logarithm.
   * @returns {number} The natural logarithm of the value.
   */
  ln(value: number): number {
    // Math.log returns NaN for non-positive values, which handles the precondition 'value > 0'.
    return Math.log(value);
  }

  /**
   * Calculates the sine of an angle.
   * @param {number} angle The angle in radians.
   * @returns {number} The sine of the angle.
   */
  sin(angle: number): number {
    return Math.sin(angle);
  }

  /**
   * Calculates the cosine of an angle.
   * @param {number} angle The angle in radians.
   * @returns {number} The cosine of the angle.
   */
  cos(angle: number): number {
    return Math.cos(angle);
  }

  /**
   * Calculates the tangent of an angle.
   * Handles cases where the angle is an odd multiple of PI/2 by returning very large numbers or NaN,
   * consistent with mathematical behavior at asymptotes.
   * @param {number} angle The angle in radians.
   * @returns {number} The tangent of the angle.
   */
  tan(angle: number): number {
    return Math.tan(angle);
  }

  /**
   * Converts an angle from degrees to radians.
   * @param {number} degrees The angle in degrees.
   * @returns {number} The angle in radians.
   */
  degreesToRadians(degrees: number): number {
    return degrees * (Math.PI / 180);
  }

  /**
   * Converts an angle from radians to degrees.
   * @param {number} radians The angle in radians.
   * @returns {number} The angle in degrees.
   */
  radiansToDegrees(radians: number): number {
    return radians * (180 / Math.PI);
  }
}

/**
 * Exports an instance of CalculatorImpl as 'calculator'.
 */
export const calculator: Calculator = new CalculatorImpl();
