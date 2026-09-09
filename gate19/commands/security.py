"""gate19 audit / security — security scanner."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.utils.console import console, success, info, warning, error
from gate19.utils.fs import find_project_root

@app.command("audit")
def audit_command(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix vulnerabilities"),
):
    """Run security audit (pip-audit if available). 🔒"""
    root = find_project_root() or Path.cwd()
    info(f"Auditing {root}...")

    # Try pip-audit
    try:
        probe = subprocess.run([sys.executable, "-m", "pip_audit", "--help"], capture_output=True, timeout=5)
        has_audit = probe.returncode == 0
    except Exception:
        has_audit = False

    # Also try `pip-audit` binary
    if not has_audit:
        import shutil
        has_audit = shutil.which("pip-audit") is not None

    if has_audit:
        cmd = [sys.executable, "-m", "pip_audit"] if not shutil.which("pip-audit") else ["pip-audit"]
        if fix:
            cmd.append("--fix")
        console.print(f"[cyan]  → Running: {' '.join(cmd)}[/]")
        result = subprocess.run(cmd, cwd=str(root))
        if result.returncode == 0:
            success("No known vulnerabilities found ✓")
        else:
            warning(f"Audit completed with code {result.returncode} — check output above")
        return

    # Fallback: check for known vulnerable patterns via pip check + simple heuristics
    warning("pip-audit not installed — running lightweight fallback checks")
    console.print("[dim]Install pip-audit for full scanning: pip install pip-audit[/]")

    # Check for outdated packages with known CVEs? fallback just warns about old versions
    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], capture_output=True, text=True, timeout=15)
        if proc.stdout.strip():
            console.print("[yellow]Outdated packages (may have security fixes):[/]")
            console.print(proc.stdout[:1500])
        else:
            console.print("[green]  ✓ No outdated packages detected[/]")
    except Exception:
        pass

    # Check for hardcoded secrets in .env
    env_path = root / ".env"
    if env_path.exists():
        text = env_path.read_text(errors="ignore")
        suspicious = []
        for line in text.splitlines():
            low = line.lower()
            if any(k in low for k in ["password", "secret", "token", "key"]) and "=" in line:
                val = line.split("=", 1)[1].strip()
                if val and val not in ("", "changeme", "secret", "password") and not val.startswith("${"):
                    # only flag if looks like real secret? skip placeholder
                    if len(val) > 8 and val.lower() not in ("true", "false"):
                        suspicious.append(line.split("=")[0].strip())
        if suspicious:
            warning(f"Potential secrets in .env: {', '.join(suspicious)} — ensure .env is in .gitignore")
        else:
            console.print("[green]  ✓ No obvious secrets in .env[/]")

    # Check .gitignore contains .env
    gitignore = root / ".gitignore"
    if gitignore.exists() and ".env" not in gitignore.read_text():
        warning(".env not in .gitignore — risk of committing secrets!")

    success("Audit fallback completed ✓")
    console.print("[dim]For full CVE scanning, run: pip install pip-audit && gate19 audit[/]")


# Alias `security`
@app.command("security")
def security_alias(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix"),
):
    """Alias for `audit`."""
    audit_command(fix=fix)
