"""Project creation integration tests — more detailed."""

from pathlib import Path
import tempfile
import os
from typer.testing import CliRunner
from gate19.cli.app import app

runner = CliRunner()

def test_project_structure_contents():
    with tempfile.TemporaryDirectory() as tmp:
        old = os.getcwd()
        os.chdir(tmp)
        try:
            result = runner.invoke(app, ["new", "demoapp", "--template", "app", "--no-install", "--no-venv"])
            assert result.exit_code == 0
            proj = Path(tmp) / "demoapp"
            # Required per spec
            for required in ["src", "tests", "docs", "assets", ".gitignore", "README.md", "pyproject.toml", "requirements.txt", ".env", "main.py"]:
                assert (proj / required).exists(), f"missing {required}"
            # .venv not created due to --no-venv, but test with venv
            # Test git init
            assert (proj / ".git").exists()
            # Test gate19.toml
            assert (proj / "gate19.toml").exists()
            # Test src package
            assert (proj / "src" / "demoapp").exists()
        finally:
            os.chdir(old)

def test_init_command():
    with tempfile.TemporaryDirectory() as tmp:
        old = os.getcwd()
        os.chdir(tmp)
        try:
            # create empty dir
            result = runner.invoke(app, ["init", "--template", "library", "--no-venv"])
            assert result.exit_code == 0
            assert (Path(tmp) / "pyproject.toml").exists()
            assert (Path(tmp) / "gate19.toml").exists()
        finally:
            os.chdir(old)

def test_all_spec_compliance():
    # Test the spec says gate19 new should produce exactly those files
    with tempfile.TemporaryDirectory() as tmp:
        old = os.getcwd()
        os.chdir(tmp)
        try:
            runner.invoke(app, ["new", "specproj", "--template", "fastapi", "--no-install", "--no-venv"])
            proj = Path(tmp) / "specproj"
            spec_files = ["src", "tests", "docs", "assets", ".gitignore", "README.md", "pyproject.toml", "requirements.txt", ".env", "main.py"]
            for f in spec_files:
                assert (proj / f).exists(), f"Spec required {f} missing"
            # Check .git was initialized
            assert (proj / ".git").exists(), ".git missing"
            # Check .venv would be created without --no-venv; test that:
            # now create another with venv
            runner.invoke(app, ["new", "specproj2", "--template", "flask", "--no-install"],)
            assert (Path(tmp) / "specproj2" / ".venv").exists()
        finally:
            os.chdir(old)
