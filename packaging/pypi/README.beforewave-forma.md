# beforewave-forma

`beforewave-forma` is a compatibility install-name package for Forma's Python
CLI. New installs should use `forma-cli`:

```bash
pipx install forma-cli
forma --help
```

This compatibility package ships the same `forma` import package, console
command, workflow compiler, runtime assets, and verifier, but user-facing docs
and examples should use the primary `forma-cli` distribution name.

Temporary run:

```bash
uvx forma-cli forma --help
```

The source repository is <https://github.com/BeforeWave/forma>.
