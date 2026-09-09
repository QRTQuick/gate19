"""CLI tests — basic help and version."""

import tempfile
from pathlib import Path
from typer.testing import CliRunner
from gate19.cli.app import app
from gate19 import __version__

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Gate19" in result.stdout or "gate19" in result.stdout.lower()
    assert "new" in result.stdout

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout

def test_python_list():
    result = runner.invoke(app, ["python", "list"])
    assert result.exit_code == 0
    assert "Python Versions" in result.stdout or "python" in result.stdout.lower()

def test_cache_info():
    result = runner.invoke(app, ["cache", "info"])
    assert result.exit_code == 0
    assert "Cache" in result.stdout

def test_doctor_runs():
    result = runner.invoke(app, ["doctor"])
    # doctor should exit 0 even if issues
    assert result.exit_code == 0
    assert "Gate19 Doctor" in result.stdout

def test_new_creates_project():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Need to cwd to tmp to avoid polluting
        import os
        old = os.getcwd()
        os.chdir(tmp)
        try:
            result = runner.invoke(app, ["new", "mytestproj", "--template", "cli", "--no-install", "--no-venv"])
            assert result.exit_code == 0, result.stdout
            proj = tmp_path / "mytestproj"
            assert proj.exists()
            assert (proj / "pyproject.toml").exists()
            assert (proj / "gate19.toml").exists()
            assert (proj / "main.py").exists()
            assert (proj / "README.md").exists()
            assert (proj / ".gitignore").exists()
            assert (proj / "requirements.txt").exists()
            assert (proj / ".env").exists()
            assert (proj / "src").exists()
            # check main.py content for cli template
            assert "typer" in (proj / "main.py").read_text() or "CLI" in (proj / "main.py").read_text()
            # check pyproject contains typer
            assert "typer" in (proj / "pyproject.toml").read_text().lower()
        finally:
            os.chdir(old)

def test_new_templates():
    templates = ["app", "api", "flask", "fastapi", "django", "pygame", "cli", "ai", "desktop", "library"]
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.getcwd()
        os.chdir(tmp)
        try:
            for tmpl in templates:
                proj_name = f"proj_{tmpl}"
                result = runner.invoke(app, ["new", proj_name, "--template", tmpl, "--no-install", "--no-venv", "--no-git"])
                assert result.exit_code == 0, f"template {tmpl} failed: {result.stdout}"
                proj = Path(tmp) / proj_name
                assert proj.exists()
                assert (proj / "main.py").exists()
                # check requirements not empty
                assert len((proj / "requirements.txt").read_text().strip()) > 0
        finally:
            os.chdir(old)

def test_new_shorthand_template():
    with tempfile.TemporaryDirectory() as tmp:
        import os
        old = os.getcwd()
        os.chdir(tmp)
        try:
            # gate19 new fastapi should infer fastapi template
            result = runner.invoke(app, ["new", "fastapi", "--no-install", "--no-venv", "--no-git"])
            assert result.exit_code == 0
            # need distinct name to avoid conflict, use api shorthand
            result2 = runner.invoke(app, ["new", "api", "--no-install", "--no-venv", "--no-git"])
            assert result2.exit_code == 0
            assert (Path(tmp) / "api" / "main.py").read_text().find("FastAPI") >= 0 or "fastapi" in (Path(tmp) / "api" / "main.py").read_text().lower()
        finally:
            os.chdir(old)
