#!/usr/bin/env node
"use strict";

const { version } = require("../package.json");
const args = process.argv.slice(2);

if (args.includes("--version") || args.includes("-v")) {
  console.log(version);
  process.exit(0);
}

console.log(`Forma is implemented as a Python CLI.

Recommended:
  pipx install forma-cli
  forma --help

Temporary run:
  uvx forma-cli forma --help

This npm package is a lightweight launcher for npm discovery. It does not
install Python dependencies automatically and is not a Node.js implementation
of Forma.
`);
