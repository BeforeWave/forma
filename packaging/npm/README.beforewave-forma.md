# @beforewave/forma

This is the npm launcher for Forma.

Forma's canonical implementation is the Python CLI package
[`forma-cli`](https://pypi.org/project/forma-cli/). This npm package exists as
a lightweight npm discovery entrypoint.

It does not install Python dependencies automatically and is not a Node.js
implementation.

## Use Forma

Recommended install:

```bash
pipx install forma-cli
forma --help
```

Temporary run:

```bash
uvx forma-cli forma --help
```

From npm:

```bash
npx @beforewave/forma
```

That command prints the Python CLI install and run instructions.
