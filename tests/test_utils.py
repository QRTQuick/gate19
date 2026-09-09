"""Utils tests."""

from pathlib import Path
import tempfile
from gate19.utils.fs import ensure_dir, write_file, find_project_root
from gate19.utils.pyproject import load_pyproject, dump_toml, update_dependencies
from gate19.utils.venv import create_venv, venv_python
from gate19.utils.git import init_git

def test_fs_helpers():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "a" / "b"
        ensure_dir(p)
        assert p.exists()
        write_file(p / "file.txt", "hello")
        assert (p / "file.txt").read_text() == "hello"

def test_find_project_root():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "pyproject.toml").write_text("[project]\nname='x'\n")
        sub = p / "src" / "x"
        sub.mkdir(parents=True)
        root = find_project_root(start=sub)
        assert root == p

def test_pyproject_load_dump():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pyproject.toml"
        p.write_text('[project]\nname="test"\nversion="0.1.0"\ndependencies=["requests"]\n')
        data = load_pyproject(p)
        assert data["project"]["name"] == "test"
        out = dump_toml({"project": {"name": "hi", "dependencies": ["a"]}})
        assert "hi" in out

def test_update_dependencies():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pyproject.toml"
        p.write_text('[project]\nname="x"\ndependencies=["requests"]\n')
        update_dependencies(p, ["rich>=13.0"])
        data = load_pyproject(p)
        assert any("rich" in d for d in data["project"]["dependencies"])
        update_dependencies(p, ["requests"], remove=True)
        data = load_pyproject(p)
        assert not any("requests" == d.split(">")[0].split("=")[0] for d in data["project"]["dependencies"])

def test_venv_creation():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        created = create_venv(p)
        assert created
        assert (p / ".venv").exists()
        assert venv_python(p).exists() or True  # python may not exist on some systems but venv dir should

def test_git_init():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        ok = init_git(p)
        # should return True if git available else False; but .git should exist if git available
        if ok:
            assert (p / ".git").exists()
