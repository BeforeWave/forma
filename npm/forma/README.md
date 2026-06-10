# @beforewave/forma

This is the npm launcher for Forma.

Forma's canonical implementation is the Python package
[`beforewave-forma`](https://pypi.org/project/beforewave-forma/). This npm
package exists as a lightweight npm discovery entrypoint and brand placeholder.
It does not install Python dependencies automatically and is not a Node.js
implementation.

## Use Forma

Recommended install:

```bash
pipx install beforewave-forma
forma --help
```

Temporary run:

```bash
uvx beforewave-forma forma --help
```

From npm:

```bash
npx @beforewave/forma
```

That command prints the Python CLI install and run instructions.

## Why This Package Exists

Forma compiles project engineering rules into dedicated agent workflows for
reviewable planning, validation, and proof. The npm package only helps npm-first
users find the canonical Python CLI.
