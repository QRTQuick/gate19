"""Commands package — imports register commands via decorators."""

# This file intentionally imports all command modules so their @app.command decorators run.
# Individual modules use `from gate19.cli.app import app`.

__all__ = [
    "new",
    "install",
    "remove",
    "update",
    "sync",
    "freeze",
    "clean",
    "doctor",
    "format",
    "lint",
    "test_cmd",
    "benchmark",
    "build",
    "publish",
    "python_mgmt",
    "cache",
    "check",
    "security",
    "run",
    "init",
]
