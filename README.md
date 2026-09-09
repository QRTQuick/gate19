# Gate19 — The Next Generation Python Project Manager

> **Fast. Smart. Developer-friendly.** Gate19 is an all-in-one Python development toolkit inspired by `uv` and Rust's `Cargo`.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/QRTQuick/gate19)

Gate19 replaces the need to juggle `pip`, `venv`, `poetry`, `black`, `ruff`, `pytest`, `build`, and `twine` separately. One tool to create, manage, test, format, build, and publish Python projects.

---

## ✨ Features

- **⚡ Project Creation** — Scaffold professional projects with `gate19 new` (10 templates)
- **🐍 Virtual Environments** — Automatic `.venv` creation without extra commands
- **📦 Smart Package Management** — Cached, parallel, conflict-aware dependency resolver
- **🌍 Python Management** — Install & switch Python versions with `gate19 python`
- **🛠️ Built-in Tools** — Format, lint, test, benchmark, audit, and clean in one CLI
- **🏗️ Build & Publish** — Wheel/sdist building and PyPI publishing
- **⚙️ Configuration** — Per-project `gate19.toml` with sensible defaults

---

## 📦 Installation

```bash
pip install gate19
# or
pipx install gate19
# or from source
pip install -e .
```

After installation, `gate19` is available globally:

```bash
gate19 --help
```

### Requirements

- Python 3.11+
- Windows / Linux / macOS

---

## 🚀 Quick Start

```bash
# Create a new project (auto-creates .venv + git + deps)
gate19 new myproject --template fastapi
cd myproject

# Or pick a template directly
gate19 new myproject --template cli

# Manage dependencies
gate19 install requests
gate19 install "fastapi[standard]"
gate19 remove requests
gate19 update
gate19 sync
gate19 freeze

# Developer tools
gate19 format        # black + isort
gate19 lint          # ruff + mypy
gate19 test          # pytest
gate19 benchmark     # performance micro-benchmarks
gate19 check         # dependency health
gate19 audit         # security scan

# Python versions
gate19 python list
gate19 python install 3.13
gate19 python use 3.13

# Build & publish
gate19 build
gate19 publish

# Utilities
gate19 clean         # remove caches, __pycache__, .venv
gate19 doctor        # diagnose project health
gate19 cache info
gate19 cache clear
```

---

## 📁 Project Structure Created by `gate19 new`

```
myproject/
├── src/
│   └── myproject/
│       └── __init__.py
├── tests/
│   └── test_main.py
├── docs/
│   └── index.md
├── assets/
│   └── .gitkeep
├── .venv/              # auto-created
├── .git/               # auto-initialized
├── .gitignore
├── README.md
├── pyproject.toml
├── requirements.txt
├── gate19.toml
├── .env
└── main.py
```

---

## 🎨 Templates

| Template | Command | Stack |
|----------|---------|-------|
| `app` / `default` | `gate19 new myapp` | requests, rich, typer, pydantic, pytest, ruff… |
| `api` | `gate19 new myapi --template api` | fastapi, uvicorn, httpx |
| `flask` | `gate19 new myapp --template flask` | flask, python-dotenv |
| `fastapi` | `gate19 new myapp --template fastapi` | fastapi, uvicorn[standard], pydantic |
| `django` | `gate19 new myapp --template django` | django, djangorestframework |
| `pygame` | `gate19 new mygame --template pygame` | pygame, rich |
| `cli` | `gate19 new mycli --template cli` | click, typer, rich, prompt-toolkit |
| `ai` | `gate19 new myai --template ai` | numpy, pandas, scikit-learn, openai |
| `desktop` | `gate19 new myapp --template desktop` | textual, rich |
| `library` | `gate19 new mylib --template library` | build, twine, pytest, mypy |

Example:

```bash
gate19 new hello --template fastapi
gate19 new hello --template django
gate19 new tools --template cli
```

All templates include common dev tools: `pytest`, `black`, `isort`, `ruff`, `mypy`.

---

## 📦 Package Management

```bash
gate19 install numpy              # add + install
gate19 install "requests>=2.28"   # version spec
gate19 install -e .               # editable
gate19 remove numpy
gate19 update                     # update all
gate19 update numpy               # update one
gate19 sync                       # sync from pyproject.toml
gate19 freeze                     # pip freeze
gate19 clean                      # clean caches
gate19 doctor                     # health check
```

Resolver features: **cached**, **parallel**, **conflict-aware**, **incremental**.

---

## 🐍 Environment Management

```bash
gate19 python list                # list available + installed
gate19 python install 3.13        # download & install Python 3.13
gate19 python install 3.12.5
gate19 python use 3.13            # switch project Python
gate19 python remove 3.12         # uninstall
```

Python installations are stored in `~/.gate19/pythons/`.

---

## 🛠️ Built-in Tools

```bash
gate19 format     # black + isort (auto-discovers files)
gate19 lint       # ruff check + mypy
gate19 test       # pytest with rich output
gate19 benchmark  # micro-benchmarks for resolver/imports
gate19 check      # dependency conflict checker
gate19 audit      # security audit (pip-audit if available)
gate19 run main.py              # run with project venv
gate19 run -- python -c "print(1)"
```

---

## 🏗️ Build

```bash
gate19 build              # wheel + sdist in dist/
gate19 build --wheel      # wheel only
gate19 build --sdist      # sdist only
```

Uses `python -m build` under the hood.

---

## 🚀 Publish

```bash
gate19 publish                    # upload dist/* to PyPI
gate19 publish --repository testpypi
gate19 publish --token $PYPI_TOKEN
```

Supports `~/.pypirc` and token auth.

---

## ⚙️ Configuration — `gate19.toml`

```toml
# gate19.toml
python = "3.13"
template = "fastapi"
auto_install = true
auto_format = true
auto_test = true

[cache]
enabled = true
dir = "~/.cache/gate19"

[resolver]
parallel = true
cache_ttl = 3600
```

CLI flags override `gate19.toml`; env vars `GATE19_*` also work.

---

## 🏛️ Architecture

```
gate19/
├── cli/            # Typer app, entry point, helpers
├── commands/       # One module per command (new, install, …)
├── templates/      # Template definitions & scaffolding
├── config/         # gate19.toml loader
├── cache/          # Download & package cache
├── resolver/       # Dependency resolver (cached, parallel)
├── python/         # Python version manager
├── installers/     # Pip-based installer abstraction
└── utils/          # Console, filesystem, venv, git, pyproject helpers
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

---

## 🔧 CLI Reference

Run `gate19 --help` or `gate19 <command> --help` for full help.

| Command | Description |
|---------|-------------|
| `new` | Create a new project |
| `init` | Initialize gate19 in existing project |
| `install` | Install packages |
| `remove` | Remove packages |
| `update` | Update packages |
| `sync` | Sync from pyproject.toml |
| `freeze` | Freeze dependencies |
| `clean` | Clean caches & artifacts |
| `doctor` | Diagnose project |
| `format` | Format with black/isort |
| `lint` | Lint with ruff/mypy |
| `test` | Run pytest |
| `benchmark` | Run benchmarks |
| `check` | Check dependency health |
| `audit` / `security` | Security scan |
| `build` | Build wheel/sdist |
| `publish` | Publish to PyPI |
| `python list/install/use/remove` | Python version mgmt |
| `cache info/clear/prune` | Cache management |
| `run` | Run command in project venv |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Run `gate19 format && gate19 lint && gate19 test`
4. Open a PR

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) (coming soon).

---

## 📄 License

MIT © Chisom Life Eke

---

## 🙏 Acknowledgments

Inspired by **uv**, **Cargo**, **Bun**, and the Python packaging community.
