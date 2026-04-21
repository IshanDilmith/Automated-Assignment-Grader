import logging
from pathlib import Path
from typing import Dict

from crewai.tools import tool


# Logging for observability
Path("logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename="logs/execution.log",
    level=logging.INFO,
    format="%(asctime)s - FILE_READER_TOOL - %(levelname)s - %(message)s",
)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".py"}


@tool("read_submission_files")
def read_submission_files(folder_path: str) -> Dict[str, str]:
    """
    Read student submission files from a folder and return them as a dictionary.

    Args:
        folder_path (str): Path to the folder containing student submissions.
            Supported file types are .txt, .md, and .py.

    Returns:
        Dict[str, str]: A dictionary where keys are student IDs (file names without
        extension) and values are the full submission text.

    Raises:
        ValueError: If the folder does not exist, is not a directory, or contains
        no valid non-empty submission files.
    """
    submissions_dir = Path(folder_path)
    logging.info("Starting file read from folder: %s", submissions_dir)

    if not submissions_dir.exists() or not submissions_dir.is_dir():
        raise ValueError(f"Invalid submissions folder: {folder_path}")

    submissions: Dict[str, str] = {}

    for file_path in sorted(submissions_dir.iterdir()):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            text = file_path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            # Fallback for rare cases where files are saved in a legacy encoding.
            text = file_path.read_text(encoding="latin-1").strip()

        if not text:
            logging.warning("Skipping empty submission file: %s", file_path.name)
            continue

        student_id = file_path.stem
        submissions[student_id] = text
        logging.info("Loaded submission for student: %s", student_id)

    if not submissions:
        raise ValueError("No valid non-empty .txt/.md/.py submission files found.")

    logging.info("Completed file read. Total submissions loaded: %d", len(submissions))
    return submissions
