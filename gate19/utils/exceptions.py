"""Custom exceptions for Gate19."""

from __future__ import annotations

class Gate19Error(Exception):
    """Base exception for Gate19."""

class ProjectExistsError(Gate19Error):
    """Project already exists."""

class TemplateNotFoundError(Gate19Error):
    """Template not found."""

class VenvCreationError(Gate19Error):
    """Virtual environment creation failed."""

class ResolverError(Gate19Error):
    """Dependency resolution failed."""

class ConfigError(Gate19Error):
    """Configuration error."""

class PythonVersionError(Gate19Error):
    """Python version management error."""
