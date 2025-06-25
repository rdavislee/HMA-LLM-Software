/**
 * @interface Calculator
 * Defines the interface for a basic calculator.
 */
export interface Calculator {
  /**
   * Adds two numbers.
   * @param a - The first number.
   * @param b - The second number.
   * @returns The sum of a and b.
   */
  add(a: number, b: number): number;

  /**
   * Subtracts the second number from the first.
   * @param a - The number to subtract from.
   * @param b - The number to subtract.
   * @returns The difference between a and b.
   */
  subtract(a: number, b: number): number;

  /**
   * Multiplies two numbers.
   * @param a - The first number.
   * @param b - The second number.
   * @returns The product of a and b.
   */
  multiply(a: number, b: number): number;

  /**
   * Divides the first number by the second.
   * @param a - The dividend.
   * @param b - The divisor.
   * @returns The quotient of a divided by b.
   */
  divide(a: number, b: number): number;

  /**
   * Calculates the power of a base to an exponent.
   * @param base - The base number.
   * @param exponent - The exponent.
   * @returns The result of base raised to the power of exponent.
   */
  power(base: number, exponent: number): number;
}
