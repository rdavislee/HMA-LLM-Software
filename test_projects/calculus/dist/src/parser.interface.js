"use strict";
/**
 * @file src/parser.interface.ts
 * @brief Defines the interface for the expression parser.
 *
 * This file specifies the contract for a parser that converts a string
 * representation of a mathematical expression into an abstract data type (ADT)
 * representing the expression.
 *
 * The parser must adhere to the standard order of operations (PEMDAS/BODMAS)
 * and support a defined set of mathematical constructs.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ParseError = void 0;
/**
 * Custom error class for parsing failures.
 * This error is thrown when the input string does not represent a valid
 * mathematical expression according to the parser's grammar rules.
 */
class ParseError extends Error {
    constructor(message) {
        super(`ParseError: ${message}`);
        this.name = 'ParseError';
    }
}
exports.ParseError = ParseError;
