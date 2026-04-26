import json
from pathlib import Path
from typing import Any, Dict

from crewai.tools import tool


@tool("load_rubric")
def load_rubric(rubric_path: str) -> Dict[str, Any]:
    """Load a rubric JSON file and return it as a dictionary."""
    path = Path(rubric_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"Rubric file not found: {rubric_path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Rubric JSON must be an object/dictionary.")

    return data
