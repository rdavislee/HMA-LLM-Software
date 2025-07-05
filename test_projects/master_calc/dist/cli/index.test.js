import { expect } from 'chai';
import sinon from 'sinon';
import { run } from '../cli/index.js'; // Updated import
describe('CLI', () => {
    let stdinStub;
    let stdoutStub;
    let exitStub;
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
        stdinStub.withArgs('line', sinon.match.func).callsFake((event, cb) => {
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
