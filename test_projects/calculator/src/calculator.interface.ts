/**
 * @interface Calculator
 * @description Defines the interface for a Calculator, providing methods for basic arithmetic,
 *              exponents, logarithms, and trigonometry.
 */
export interface Calculator {
  /**
   * Adds two numbers.
   * @param {number} a The first number.
   * @param {number} b The second number.
   * @returns {number} The sum of a and b.
   * @precondition a and b are valid numbers.
   * @postcondition Returns a + b.
   */
  add(a: number, b: number): number;

  /**
   * Subtracts the second number from the first.
   * @param {number} a The first number (minuend).
   * @param {number} b The second number (subtrahend).
   * @returns {number} The difference of a and b.
   * @precondition a and b are valid numbers.
   * @postcondition Returns a - b.
   */
  subtract(a: number, b: number): number;

  /**
   * Multiplies two numbers.
   * @param {number} a The first number.
   * @param {number} b The second number.
   * @returns {number} The product of a and b.
   * @precondition a and b are valid numbers.
   * @postcondition Returns a * b.
   */
  multiply(a: number, b: number): number;

  /**
   * Divides the first number by the second.
   * @param {number} a The dividend.
   * @param {number} b The divisor.
   * @returns {number} The quotient of a divided by b.
   * @precondition b must not be zero.
   * @postcondition Returns a / b. Throws an error or returns Infinity/NaN if b is zero.
   */
  divide(a: number, b: number): number;

  /**
   * Calculates the result of a base raised to an exponent.
   * @param {number} base The base number.
   * @param {number} exponent The exponent.
   * @returns {number} The result of base^exponent.
   * @precondition base and exponent are valid numbers.
   * @postcondition Returns base raised to the power of exponent.
   */
  power(base: number, exponent: number): number;

  /**
   * Calculates the logarithm of a value to a specified base.
   * @param {number} base The base of the logarithm.
   * @param {number} value The value for which to calculate the logarithm.
   * @returns {number} The logarithm of value to the given base.
   * @precondition base > 0 and base !== 1. value > 0.
   * @postcondition Returns log_base(value).
   */
  log(base: number, value: number): number;

  /**
   * Calculates the natural logarithm (base e) of a value.
   * @param {number} value The value for which to calculate the natural logarithm.
   * @returns {number} The natural logarithm of the value.
   * @precondition value > 0.
   * @postcondition Returns ln(value).
   */
  ln(value: number): number;

  /**
   * Calculates the sine of an angle.
   * @param {number} angle The angle in radians.
   * @returns {number} The sine of the angle.
   * @precondition angle is a valid number.
   * @postcondition Returns sin(angle).
   */
  sin(angle: number): number;

  /**
   * Calculates the cosine of an angle.
   * @param {number} angle The angle in radians.
   * @returns {number} The cosine of the angle.
   * @precondition angle is a valid number.
   * @postcondition Returns cos(angle).
   */
  cos(angle: number): number;

  /**
   * Calculates the tangent of an angle.
   * @param {number} angle The angle in radians.
   * @returns {number} The tangent of the angle.
   * @precondition angle is a valid number. Angle should not be an odd multiple of PI/2.
   * @postcondition Returns tan(angle).
   */
  tan(angle: number): number;

  /**
   * Converts an angle from degrees to radians.
   * @param {number} degrees The angle in degrees.
   * @returns {number} The angle in radians.
   * @precondition degrees is a valid number.
   * @postcondition Returns the equivalent angle in radians.
   */
  degreesToRadians(degrees: number): number;

  /**
   * Converts an angle from radians to degrees.
   * @param {number} radians The angle in radians.
   * @returns {number} The angle in degrees.
   * @precondition radians is a valid number.
   * @postcondition Returns the equivalent angle in degrees.
   */
  radiansToDegrees(radians: number): number;
}