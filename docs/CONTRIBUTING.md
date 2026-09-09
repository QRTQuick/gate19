# Contributing to Gate19

Thanks for your interest! Gate19 aims to be the fastest Python project manager.

## Setup

```bash
git clone https://github.com/QRTQuick/gate19.git
cd gate19
pip install -e ".[dev]"
```

## Workflow

1. Fork & branch (`feature/my-feature`)
2. Code with type hints, dataclasses, logging
3. Test:

```bash
gate19 format
gate19 lint
gate19 test
gate19 doctor
```

Or directly:

```bash
black gate19 tests
ruff check gate19
mypy gate19
pytest -v
```

4. Open PR against `main`

## Code Style

- Python 3.11+
- `black` line 100, `isort`, `ruff`
- Type hints required
- Rich for CLI output
- One module per command under `gate19/commands/`

## Adding a Template

Edit `gate19/templates/definitions.py`:

```python
"mytemplate": Template(
    name="mytemplate",
    description="...",
    dependencies=[...],
    dev_dependencies=[...],
)
```

Add factory in `_MAIN_FACTORIES`.

## Adding a Command

Create `gate19/commands/mycommand.py`:

```python
import typer
from gate19.cli.app import app
@app.command("mycommand")
def mycommand(...):
    """Help."""
    ...
```

Import it in `gate19/cli/app.py`.

## Testing

- `tests/` mirrors `gate19/`
- Run `pytest tests -v --cov`
- Add integration tests using `typer.testing.CliRunner`

## Release

- Bump version in `gate19/__init__.py` and `pyproject.toml`
- `gate19 build`
- `gate19 publish --dry-run`
- Tag & push

## Code of Conduct

Be kind, inclusive, and help newcomers. See `CODE_OF_CONDUCT.md` (if present).

## License

By contributing you agree to MIT.
