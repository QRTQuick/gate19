# Architecture — Gate19

## Design Principles

- **Modular**: one module per command
- **Fast**: cached, parallel, incremental
- **Compatibility**: pip/build/twine compatible
- **Developer Experience**: rich output, helpful errors, progress bars

## Layout

```
gate19/
├── cli/
│   └── app.py          # Typer app, version callback, help table
├── commands/           # One file per command
│   ├── new.py          # scaffolding, venv, git
│   ├── install.py      # pip wrapper + pyproject update
│   ├── remove.py
│   ├── update.py
│   ├── sync.py
│   ├── freeze.py
│   ├── clean.py
│   ├── doctor.py
│   ├── format.py       # black/isort/ruff wrappers
│   ├── lint.py
│   ├── test_cmd.py
│   ├── benchmark.py
│   ├── build.py        # python -m build
│   ├── publish.py      # twine
│   ├── python_mgmt.py  # PythonManager
│   ├── cache.py
│   ├── check.py        # resolver health
│   ├── security.py     # pip-audit fallback
│   └── run.py          # venv exec
├── templates/
│   └── definitions.py  # TEMPLATES dict, render_main_py()
├── config/
│   └── manager.py      # gate19.toml loader, env overrides
├── cache/
│   └── manager.py      # file cache with TTL
├── resolver/
│   └── resolver.py     # parallel, cached, conflict-aware
├── python/
│   └── manager.py      # Python version shim manager
├── installers/
│   └── installer.py    # pip abstraction
└── utils/
    ├── console.py      # rich console, icons
    ├── fs.py           # filesystem helpers
    ├── venv.py         # venv creation & pip detection
    ├── git.py          # git init
    ├── pyproject.py    # toml load/dump, dep updates
    └── constants.py
```

## Key Flows

### `gate19 new`

1. Normalize name/template, infer shorthand
2. Create dirs (src/pkg, tests, docs, assets)
3. Render `main.py` via `render_main_py(template, name)`
4. Write `pyproject.toml`, `requirements.txt`, `gate19.toml`, `README`, `.gitignore`, `.env`
5. `git init`
6. `venv` via `python -m venv`
7. Auto-install deps via `Installer.install()` → resolver → pip

### Resolver

- Cache key: sorted requirements
- Parallel fetch from PyPI JSON (`httpx`) with fallback synthetic versions
- Conflict detection: duplicate names with `==` specifiers
- Cached result stored via `CacheManager`

### Installer

- Detects venv pip else global pip
- PEP 668 fallback (`--break-system-packages`)
- Rich progress bar
- Updates `pyproject.toml` + `requirements.txt`

### PythonManager

- Install root `~/.gate19/pythons/python-X.Y.Z`
- Shim `bin/python` delegating to system python (real standalone download omitted for portability)
- `use` updates `gate19.toml` + `.python-version`

### Config

- `gate19.toml` loaded with `tomllib`, env overrides `GATE19_*`
- Defaults merged
- `write_default_config()` for scaffolding

## Performance Optimizations

- Multiprocessing/threadpool for resolver fetching
- Async httpx
- File cache with TTL
- Incremental installs (only new deps)
- Fast startup: lazy imports in commands, no heavy work in `cli.app`

## Error Handling

- `typer.Exit` with helpful messages via `console`
- Fallbacks: format → trailing-whitespace, lint → py_compile, test → unittest, audit → heuristic
- Never crash on missing optional tools

## Future Extensibility

- Add new template: edit `TEMPLATES` dict
- Add new command: create `commands/foo.py` with `@app.command("foo")`
- Resolver: replace synthetic fallback with full PyPI Simple API parsing
- Cache: add sqlite backend
