import json
from pathlib import Path


def ensure_directory(folder_path):
    """Create folder if it doesn't exist."""
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def load_json(file_path):
    """Load a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, file_path):
    """Save dictionary as JSON."""
    ensure_directory(Path(file_path).parent)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)