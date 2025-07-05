/**
 * Custom error class for application-specific errors in the symbolic calculator.
 * All errors originating from the calculator's core logic (parsing, evaluation,
 * differentiation, integration, simplification) should throw an instance of this class.
 *
 * This allows for easy identification and handling of application-specific errors
 * distinct from generic JavaScript errors.
 */
export class CalculatorError extends Error {
    /**
     * Creates an instance of CalculatorError.
     * @param message - A descriptive error message.
     * @param options - Optional parameters.
     * @param options.cause - The underlying cause of the error, if any (e.g., another error object).
     */
    constructor(message, options) {
        // The `Error` constructor in the configured TS target (likely pre-ES2022)
        // does not support the second 'options' argument. Calling with only the message.
        super(message);
        this.name = 'CalculatorError';
        // Set the prototype explicitly to ensure instanceof works correctly in TypeScript
        // This is a common pattern for custom errors extending built-in Error.
        Object.setPrototypeOf(this, CalculatorError.prototype);
    }
}
