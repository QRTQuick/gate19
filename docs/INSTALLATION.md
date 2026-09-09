# Installation Guide — Gate19

## Requirements

- Python 3.11+
- pip / pipx
- Git (optional, for `gate19 new` auto-init)

Gate19 supports Windows, Linux, and macOS.

## Install from PyPI

```bash
pip install gate19
# or isolated
pipx install gate19
```

After install, verify:

```bash
gate19 --version
gate19 --help
```

## Install from Source

```bash
git clone https://github.com/QRTQuick/gate19.git
cd gate19
pip install -e .
gate19 --help
```

## Development Install

```bash
pip install -e ".[dev]"
gate19 test
gate19 lint
gate19 format
```

## Shell Completion

```bash
gate19 --install-completion
# restart shell
```

## Upgrading

```bash
pip install --upgrade gate19
# or
pipx upgrade gate19
```

## Uninstall

```bash
pip uninstall gate19
# or
pipx uninstall gate19
```

## Docker (optional)

```dockerfile
FROM python:3.11-slim
RUN pip install gate19
CMD ["gate19", "--help"]
```

## Troubleshooting

- **externally-managed-environment** on Debian/Ubuntu: use `pip install --break-system-packages gate19` or `pipx`
- **command not found**: ensure `~/.local/bin` is on PATH
- **build failures**: `pip install build hatchling` manually
