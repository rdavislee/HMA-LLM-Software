module.exports = {
  createHighlighter: jest.fn().mockResolvedValue({
    codeToHtml: jest.fn().mockReturnValue('<pre><code>mocked code</code></pre>'),
    loadTheme: jest.fn(),
    loadLanguage: jest.fn(),
  }),
  bundledLanguages: {},
  bundledThemes: {},
};