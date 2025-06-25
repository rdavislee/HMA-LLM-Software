import { expect } from 'chai';
import { add, subtract, multiply, divide } from '../src/index';

describe('Calculator', () => {
  it('adds two numbers', () => {
    expect(add(2, 3)).to.equal(5);
  });

  it('subtracts two numbers', () => {
    expect(subtract(5, 3)).to.equal(2);
  });

  it('multiplies two numbers', () => {
    expect(multiply(4, 3)).to.equal(12);
  });

  it('divides two numbers', () => {
    expect(divide(10, 2)).to.equal(5);
  });

  it('throws on divide by zero', () => {
    expect(() => divide(1, 0)).to.throw('Division by zero');
  });
}); 