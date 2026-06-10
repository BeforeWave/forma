#!/usr/bin/env node
"use strict";

const version = "0.1.1";
const args = process.argv.slice(2);

if (args.includes("--version") || args.includes("-v")) {
  console.log(version);
  process.exit(0);
}

console.log(`Forma is implemented as a Python CLI.

Recommended:
  pipx install beforewave-forma
  forma --help

Temporary run:
  uvx beforewave-forma forma --help

This npm package is a lightweight launcher for npm discovery. It does not
install Python dependencies automatically and is not a Node.js implementation
of Forma.
`);
