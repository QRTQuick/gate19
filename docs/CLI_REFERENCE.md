# CLI Reference — Gate19

> Generated for `gate19 v0.1.0`. Run `gate19 <command> --help` for latest.

## Global Options

```
gate19 --help
gate19 --version
gate19 --verbose
```

## `gate19 new`

Create a new project.

```bash
gate19 new <name> [options]
gate19 new myapp --template fastapi --python 3.13
gate19 new api  # shorthand: template = api
```

Options:
- `--template, -t` — app, api, flask, fastapi, django, pygame, cli, ai, desktop, library
- `--python, -p` — Python version (default 3.11)
- `--no-install` — skip deps install
- `--no-git` — skip git init
- `--no-venv` — skip venv
- `--force, -f` — overwrite

Creates: `src/ tests/ docs/ assets/ .gitignore README.md pyproject.toml requirements.txt gate19.toml .env main.py .venv .git`

## `gate19 init`

Initialize gate19 in existing directory.

```bash
gate19 init --template cli --python 3.12
```

## Package Management

```bash
gate19 install <packages...>        # e.g. gate19 install requests "fastapi>=0.110"
gate19 install                      # sync from pyproject.toml
gate19 remove <packages...>         # or uninstall
gate19 update [packages...]         # update all or specific
gate19 sync [--check]
gate19 freeze [-o file.txt]
gate19 clean [--all|--venv|--cache] [--dry-run]
gate19 doctor [--fix]
```

## Python Management

```bash
gate19 python list
gate19 python install 3.13
gate19 python install 3.12.5
gate19 python use 3.13 [--project PATH]
gate19 python remove 3.12
```

Installs to `~/.gate19/pythons/`.

## Tools

```bash
gate19 format [path] [--check]
gate19 lint [path] [--fix]
gate19 test [args...] [-v] [--coverage]
gate19 benchmark [--iter N]
gate19 check
gate19 audit [--fix]        # or gate19 security
gate19 run <command>        # run in project venv
gate19 run main.py
gate19 run -- pytest -v
```

## Build & Publish

```bash
gate19 build [--wheel] [--sdist] [--outdir dist]
gate19 publish [--repository pypi|testpypi] [--token TOKEN] [--skip-build] [--dry-run]
```

## Cache

```bash
gate19 cache          # same as cache info
gate19 cache info
gate19 cache clear [--yes]
gate19 cache prune [--days 7]
```

## Config

`gate19.toml` at project root:

```toml
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

CLI flags > gate19.toml > env `GATE19_*` > defaults.

## Examples

```bash
gate19 new hello --template cli
cd hello
gate19 install rich
gate19 run main.py
gate19 test --coverage
gate19 build
gate19 publish --dry-run
```
