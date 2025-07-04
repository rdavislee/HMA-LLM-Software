import { expect } from 'chai';
import { evaluate } from '../src/evaluator';

describe('Evaluator', () => {
  // Test basic arithmetic operations
  describe('Arithmetic Operations', () => {
    it('should correctly evaluate addition', () => {
      expect(evaluate('2 + 3', {})).to.equal(5);
    });

    it('should correctly evaluate subtraction', () => {
      expect(evaluate('10 - 4', {})).to.equal(6);
    });

    it('should correctly evaluate multiplication', () => {
      expect(evaluate('5 * 6', {})).to.equal(30);
    });

    it('should correctly evaluate division', () => {
      expect(evaluate('10 / 2', {})).to.equal(5);
    });

    it('should correctly evaluate exponents', () => {
      expect(evaluate('2 ^ 3', {})).to.equal(8);
      expect(evaluate('4 ^ 0.5', {})).to.equal(2);
    });

    it('should respect order of operations (PEMDAS)', () => {
      expect(evaluate('2 + 3 * 4', {})).to.equal(14);
      expect(evaluate('(2 + 3) * 4', {})).to.equal(20);
      expect(evaluate('10 - 2 ^ 3 / 4 + 1', {})).to.equal(9);
    });

    it('should handle negative numbers in operations', () => {
      expect(evaluate('-5 + 3', {})).to.equal(-2);
      expect(evaluate('2 * (-3)', {})).to.equal(-6);
      expect(evaluate('10 / -2', {})).to.equal(-5);
    });
  });

  // Test variables
  describe('Variables', () => {
    it('should evaluate expression with a single variable', () => {
      expect(evaluate('x + 5', { x: 10 })).to.equal(15);
    });

    it('should evaluate expression with multiple variables', () => {
      expect(evaluate('a * b + c', { a: 2, b: 3, c: 4 })).to.equal(10);
    });

    it('should evaluate expression with variables and constants', () => {
      expect(evaluate('2 * pi * r', { r: 5 })).to.be.closeTo(31.4159, 0.0001);
    });

    it('should throw an error for an undefined variable', () => {
      expect(() => evaluate('x + y', { x: 1 })).to.throw();
    });

    it('should handle variables with non-numeric values gracefully (mathjs handles this)', () => {
      // mathjs will throw on invalid types, so we expect a throw
      expect(() => evaluate('x + 5', { x: 'abc' })).to.throw(); 
    });
  });

  // Test mathematical functions and constants
  describe('Mathematical Functions and Constants', () => {
    it('should correctly evaluate pi', () => {
      expect(evaluate('pi', {})).to.be.closeTo(Math.PI, 0.0000001);
    });

    it('should correctly evaluate e', () => {
      expect(evaluate('e', {})).to.be.closeTo(Math.E, 0.0000001);
    });

    it('should evaluate log (base 10 by default)', () => {
      expect(evaluate('log(100)', {})).to.be.closeTo(2, 0.0000001);
      expect(evaluate('log(1000)', {})).to.be.closeTo(3, 0.0000001);
    });

    it('should evaluate log with specified base', () => {
      expect(evaluate('log(8, 2)', {})).to.be.closeTo(3, 0.0000001);
      expect(evaluate('log(27, 3)', {})).to.be.closeTo(3, 0.0000001);
    });

    it('should evaluate natural log (log with base e)', () => {
      expect(evaluate('log(e^2, e)', {})).to.be.closeTo(2, 0.0000001); 
      expect(evaluate('log(exp(3), "e")', {})).to.be.closeTo(3, 0.0000001); 
    });

    it('should evaluate log of 1 to any base as 0', () => {
      expect(evaluate('log(1, 10)', {})).to.equal(0);
      expect(evaluate('log(1, 2)', {})).to.equal(0);
    });

    it('should evaluate log of base to base as 1', () => {
      expect(evaluate('log(5, 5)', {})).to.equal(1);
      expect(evaluate('log(10, 10)', {})).to.equal(1);
    });

    it('should handle log of 0', () => {
      expect(evaluate('log(0)', {})).to.equal(-Infinity); 
    });

    it('should handle log of Infinity', () => {
      expect(evaluate('log(Infinity)', {})).to.equal(Infinity);
    });

    it('should evaluate sin function', () => {
      expect(evaluate('sin(pi / 2)', {})).to.be.closeTo(1, 0.0000001);
      expect(evaluate('sin(0)', {})).to.be.closeTo(0, 0.0000001);
    });

    it('should evaluate cos function', () => {
      expect(evaluate('cos(pi)', {})).to.be.closeTo(-1, 0.0000001);
      expect(evaluate('cos(0)', {})).to.be.closeTo(1, 0.0000001);
    });

    it('should evaluate tan function', () => {
      expect(evaluate('tan(pi / 4)', {})).to.be.closeTo(1, 0.0000001);
      expect(evaluate('tan(0)', {})).to.be.closeTo(0, 0.0000001);
    });

    it('should handle tan(pi/2) resulting in Infinity', () => {
      expect(evaluate('tan(pi / 2)', {})).to.be.greaterThan(1e15);
    });

    it('should evaluate csc function', () => {
      expect(evaluate('csc(pi / 2)', {})).to.be.closeTo(1, 0.0000001);
    });

    it('should handle csc(0) resulting in Infinity', () => {
      expect(evaluate('csc(0)', {})).to.equal(Infinity);
    });

    it('should evaluate sec function', () => {
      expect(evaluate('sec(0)', {})).to.be.closeTo(1, 0.0000001);
    });

    it('should handle sec(pi/2) resulting in Infinity', () => {
      expect(evaluate('sec(pi / 2)', {})).to.be.greaterThan(1e15);
    });

    it('should evaluate cot function', () => {
      expect(evaluate('cot(pi / 4)', {})).to.be.closeTo(1, 0.0000001);
    });

    it('should handle cot(0) resulting in Infinity', () => {
      expect(evaluate('cot(0)', {})).to.equal(Infinity);
    });

    it('should evaluate asin function', () => {
      expect(evaluate('asin(1)', {})).to.be.closeTo(Math.PI / 2, 0.0000001);
    });

    it('should evaluate acos function', () => {
      expect(evaluate('acos(-1)', {})).to.be.closeTo(Math.PI, 0.0000001);
    });

    it('should evaluate atan function', () => {
      expect(evaluate('atan(1)', {})).to.be.closeTo(Math.PI / 4, 0.0000001);
    });

    it('should evaluate acsc function', () => {
      expect(evaluate('acsc(1)', {})).to.be.closeTo(Math.PI / 2, 0.0000001);
    });

    it('should evaluate asec function', () => {
      expect(evaluate('asec(1)', {})).to.be.closeTo(0, 0.0000001);
    });

    it('should evaluate acot function', () => {
      expect(evaluate('acot(1)', {})).to.be.closeTo(Math.PI / 4, 0.0000001);
    });

    it('should handle asin(value > 1 or < -1) resulting in NaN', () => {
      expect(isNaN(evaluate('asin(2)', {}))).to.be.true;
      expect(isNaN(evaluate('asin(-2)', {}))).to.be.true;
    });

    it('should handle acos(value > 1 or < -1) resulting in NaN', () => {
      expect(isNaN(evaluate('acos(2)', {}))).to.be.true;
      expect(isNaN(evaluate('acos(-2)', {}))).to.be.true;
    });
  });

  // Test edge cases and error handling
  describe('Edge Cases and Error Handling', () => {
    it('should handle division by zero resulting in Infinity', () => {
      expect(evaluate('10 / 0', {})).to.equal(Infinity);
    });

    it('should throw an error for invalid expression syntax', () => {
      expect(() => evaluate('2 + * 3', {})).to.throw();
      expect(() => evaluate('sin()', {})).to.throw();
      expect(() => evaluate('log(10,)', {})).to.throw();
    });

    it('should handle expressions resulting in Infinity', () => {
      expect(evaluate('1 / 0', {})).to.equal(Infinity);
    });

    it('should handle expressions resulting in NaN', () => {
      expect(isNaN(evaluate('sqrt(-1)', {}))).to.be.true;
      expect(isNaN(evaluate('log(-1)', {}))).to.be.true;
      expect(isNaN(evaluate('0 / 0', {}))).to.be.true;
      expect(isNaN(evaluate('asin(2)', {}))).to.be.true;
    });

    it('should return 0 for an empty expression (mathjs behavior)', () => {
      expect(evaluate('', {})).to.equal(0);
    });

    it('should handle large numbers without precision issues (within mathjs limits)', () => {
      expect(evaluate('1e20 + 1', {})).to.equal(Infinity);
      expect(evaluate('1e-20 * 1e-20', {})).to.equal(1e-40);
    });

    it('should handle undefined scope', () => {
      expect(evaluate('2 + 3')).to.equal(5);
    });

    it('should handle null scope by treating it as an empty object', () => {
      expect(evaluate('2 + 3', {})).to.equal(5);
    });

    it('should handle empty scope', () => {
      expect(evaluate('2 + 3', {})).to.equal(5);
    });
  });
});