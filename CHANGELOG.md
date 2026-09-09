# Changelog

All notable changes to Gate19 will be documented here.

## [0.1.0] - 2026-09-09

### Added
- Initial release of Gate19 — The Next Generation Python Project Manager
- `gate19 new` with 10 templates: app, api, flask, fastapi, django, pygame, cli, ai, desktop, library
- Automatic `.venv` creation and `git init`
- Smart dependency installation per template
- Package management: `install`, `remove`, `update`, `sync`, `freeze`, `clean`, `doctor`
- Python version management: `python list/install/use/remove`
- Developer tools: `format`, `lint`, `test`, `benchmark`, `check`, `audit`, `run`
- Build system: `gate19 build` (wheel + sdist)
- Publishing: `gate19 publish` to PyPI
- High-performance resolver: cached, parallel, conflict-aware
- Configuration via `gate19.toml`
- Rich CLI with Typer, progress bars, tables, icons
- Modular architecture
- Documentation, CI/CD, tests

