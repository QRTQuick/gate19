"""Config tests."""

from pathlib import Path
import tempfile
from gate19.config.manager import Config, load_config, write_default_config

def test_load_default_when_missing():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = load_config(Path(tmp))
        assert cfg.python == "3.11"
        assert cfg.template == "app"

def test_write_and_load():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        write_default_config(p, python="3.13", template="fastapi")
        assert (p / "gate19.toml").exists()
        cfg = load_config(p)
        assert cfg.python == "3.13"
        assert cfg.template == "fastapi"

def test_config_from_dict():
    cfg = Config.from_dict({"python": "3.12", "template": "cli", "auto_install": False})
    assert cfg.python == "3.12"
    assert cfg.template == "cli"
    assert cfg.auto_install is False
