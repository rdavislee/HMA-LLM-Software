export interface ICalculator {
  /**
   * Adds two numbers.
   * @param a The first number.
   * @param b The second number.
   * @returns The sum of a and b.
   */
  add(a: number, b: number): number;

  /**
   * Subtracts the second number from the first.
   * @param a The first number.
   * @param b The second number.
   * @returns The difference of a and b.
   */
  subtract(a: number, b: number): number;

  /**
   * Multiplies two numbers.
   * @param a The first number.
   * @param b The second number.
   * @returns The product of a and b.
   */
  multiply(a: number, b: number): number;

  /**
   * Divides the first number by the second.
   * @param a The numerator.
   * @param b The denominator. Cannot be zero.
   * @returns The quotient of a and b.
   */
  divide(a: number, b: number): number;

  /**
   * Raises a base to an exponent power (base^exponent).
   * @param base The base number.
   * @param exponent The exponent.
   * @returns The result of base raised to the exponent.
   */
  power(base: number, exponent: number): number;

  /**
   * Calculates the logarithm of a number with a specified base.
   * @param num The number for which to calculate the logarithm.
   * @param base The base of the logarithm.
   * @returns The logarithm of num with the given base.
   */
  log(num: number, base: number): number;

  /**
   * Calculates the natural logarithm (base e) of a number.
   * @param num The number for which to calculate the natural logarithm.
   * @returns The natural logarithm of num.
   */
  naturalLog(num: number): number;

  /**
   * Calculates the sine of an angle (in radians).
   * @param angleInRadians The angle in radians.
   * @returns The sine of the angle.
   */
  sin(angleInRadians: number): number;

  /**
   * Calculates the cosine of an angle (in radians).
   * @param angleInRadians The angle in radians.
   * @returns The cosine of the angle.
   */
  cos(angleInRadians: number): number;

  /**
   * Calculates the tangent of an angle (in radians).
   * @param angleInRadians The angle in radians.
   * @returns The tangent of the angle.
   */
  tan(angleInRadians: number): number;

  /**
   * Converts an angle from degrees to radians.
   * @param degrees The angle in degrees.
   * @returns The angle in radians.
   */
  degreesToRadians(degrees: number): number;

  /**
   * Converts an angle from radians to degrees.
   * @param radians The angle in radians.
   * @returns The angle in degrees.
   */
  radiansToDegrees(radians: number): number;
}