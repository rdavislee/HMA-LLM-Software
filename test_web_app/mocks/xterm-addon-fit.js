module.exports = {
  FitAddon: jest.fn().mockImplementation(() => ({
    fit: jest.fn(),
    dispose: jest.fn(),
    activate: jest.fn(),
  })),
  WebLinksAddon: jest.fn().mockImplementation(() => ({
    activate: jest.fn(),
    dispose: jest.fn(),
  })),
};