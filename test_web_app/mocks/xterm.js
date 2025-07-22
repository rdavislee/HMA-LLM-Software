module.exports = {
  Terminal: jest.fn().mockImplementation(() => ({
    open: jest.fn(),
    write: jest.fn(),
    writeln: jest.fn(),
    clear: jest.fn(),
    dispose: jest.fn(),
    onData: jest.fn(),
    onKey: jest.fn(),
    onResize: jest.fn(),
    resize: jest.fn(),
    focus: jest.fn(),
    blur: jest.fn(),
    loadAddon: jest.fn(),
    options: {},
    element: document.createElement('div'),
    textarea: document.createElement('textarea'),
  })),
};