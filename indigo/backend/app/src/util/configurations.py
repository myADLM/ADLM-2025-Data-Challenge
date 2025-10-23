"""
Configuration utilities for loading YAML config files.

This module provides functions to locate and load configuration files
from the app's config directory.
"""

from pathlib import Path

import yaml


def load_config(file_name: str) -> dict:
    """Load a YAML configuration file from the app's config directory."""
    config_path = get_app_root() / "config" / file_name
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_app_root() -> Path:
    """Find the app root directory by traversing up from current file."""
    parents = Path(__file__).resolve().parents
    for parent in parents:
        if parent.name == "app":
            return parent
    raise ValueError("App root not found")
