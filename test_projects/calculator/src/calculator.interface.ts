/**
 * @interface Calculator
 * Defines the contract for a calculator, specifying basic arithmetic operations.
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
   * @returns The difference of a and b.
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
   * @returns The quotient of a and b.
   * @throws An error if the divisor (b) is zero.
   */
  divide(a: number, b: number): number;

  /**
   * Raises the first number to the power of the second number.
   * @param base - The base number.
   * @param exponent - The exponent.
   * @returns The base raised to the power of the exponent.
   */
  power(base: number, exponent: number): number;
}
