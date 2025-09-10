from pathlib import Path
import yaml

def load_config(file_name: str) -> dict:
    return get_app_root() / "config" / file_name
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_app_root() -> Path:
    parents = Path(__file__).resolve().parents
    for parent in parents:
        if parent.name == "app":
            return parent
    raise ValueError("App root not found")
    