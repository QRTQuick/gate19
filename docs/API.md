# API Documentation — Gate19

Programmatic use (import gate19 as library).

## Console

```python
from gate19.utils.console import console, success, error, warning, info
success("done")
console.print("[green]hi[/]")
```

## Templates

```python
from gate19.templates.definitions import TEMPLATES, get_template, render_main_py, all_dependencies
tmpl = get_template("fastapi")
print(tmpl.dependencies)
print(render_main_py("cli", "myapp"))
```

## Resolver

```python
from gate19.resolver.resolver import Resolver
r = Resolver()
result = r.resolve(["requests>=2.0", "rich"], parallel=True)
print(result.packages, result.conflicts, result.elapsed)
```

## Cache

```python
from gate19.cache.manager import CacheManager
cm = CacheManager()
cm.set("key", {"a": 1})
print(cm.get("key"))
print(cm.info())
cm.clear()
```

## Config

```python
from gate19.config.manager import load_config
cfg = load_config(project_root=Path.cwd())
print(cfg.python, cfg.template)
```

## Installer

```python
from gate19.installers.installer import Installer
inst = Installer(Path.cwd())
inst.install(["requests"])
inst.freeze()
```

## Python Manager

```python
from gate19.python.manager import PythonManager
pm = PythonManager()
pm.install("3.13")
pm.use("3.13")
pm.list_installed()
```

## Project Creation (programmatic)

```python
from pathlib import Path
from gate19.templates.definitions import render_main_py
from gate19.utils.fs import ensure_dir, write_file

# see gate19.commands.new for full scaffolding
```

## Utilities

- `gate19.utils.fs`: `ensure_dir`, `write_file`, `find_project_root`
- `gate19.utils.venv`: `create_venv`, `venv_python`, `venv_pip`
- `gate19.utils.pyproject`: `load_pyproject`, `dump_toml`, `update_dependencies`
- `gate19.utils.git`: `init_git`
