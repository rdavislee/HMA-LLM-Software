import { expect } from 'chai';
import sinon from 'sinon';
import { run } from '../cli/index.js'; // Updated import

// Mock dependencies to isolate CLI testing
// These are not directly used in this specific test, but they are common dependencies of the CLI
// and serve as examples for .js extension.
import { tokenize } from '../parser/tokenizer.js';
import { parse } from '../parser/parser.js';
import { evaluate } from '../operations/evaluate.js';
import { differentiate } from '../operations/differentiate.js';
import { integrate } from '../operations/integrate.js';
import { simplify } from '../operations/simplify.js';

describe('CLI', () => {
  let stdinStub: sinon.SinonStub;
  let stdoutStub: sinon.SinonStub;
  let exitStub: sinon.SinonStub;

  beforeEach(() => {
    stdinStub = sinon.stub(process.stdin, 'on');
    stdoutStub = sinon.stub(process.stdout, 'write');
    exitStub = sinon.stub(process, 'exit');
  });

  afterEach(() => {
    stdinStub.restore();
    stdoutStub.restore();
    exitStub.restore();
  });

  it('should display a welcome message and prompt for input', () => {
    // Simulate user input for a single loop iteration to exit cleanly
    stdinStub.withArgs('line', sinon.match.func).callsFake((event: string, cb: (input: string) => void) => {
      if (event === 'line') {
        cb('exit'); // Simulate typing 'exit'
      }
    });

    run();

    expect(stdoutStub.calledWith(sinon.match(/Welcome to the Symbolic Calculator/))).to.be.true;
    expect(stdoutStub.calledWith(sinon.match(/Enter an expression/))).to.be.true;
    expect(exitStub.calledWith(0)).to.be.true;
  });
});