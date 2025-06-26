# Vendored NPM Packages for Offline TypeScript Environment

This directory stores **tarball (.tgz) files** that have been generated with `npm pack` on a machine that has Internet access. Keeping these tarballs in-repo lets the sandboxed agents install TypeScript tooling _without any network access_.

Place the following files here (exact versions suggested by `notes.md`):

- typescript-5.3.3.tgz
- ts-node-10.9.1.tgz
- tsx-4.7.0.tgz
- @types/node-20.11.0.tgz
- mocha-10.2.0.tgz
- chai-4.3.8.tgz
- @types/mocha-10.0.6.tgz
- @types/chai-4.3.11.tgz

The upcoming `scripts/install_local_typescript.py` helper will install everything from this folder to `.node_deps/` at workspace start-up. 