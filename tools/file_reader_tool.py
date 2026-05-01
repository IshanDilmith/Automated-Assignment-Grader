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

SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".pdf", ".docx", ".doc"}


def extract_text_from_pdf(path: Path) -> str:
    try:
        import PyPDF2
    except Exception:
        logging.error("PyPDF2 not installed; cannot extract text from PDF: %s", path.name)
        return ""

    try:
        with path.open("rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            texts = []
            for page in reader.pages:
                try:
                    txt = page.extract_text() or ""
                except Exception:
                    txt = ""
                texts.append(txt)
            return "\n".join(texts).strip()
    except Exception as e:
        logging.error("Failed to extract PDF text for %s: %s", path.name, e)
        return ""


def extract_text_from_docx(path: Path) -> str:
    try:
        import docx
    except Exception:
        logging.error("python-docx not installed; cannot extract text from DOCX: %s", path.name)
        return ""

    try:
        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        logging.error("Failed to extract DOCX text for %s: %s", path.name, e)
        return ""


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

        suffix = file_path.suffix.lower()
        text = ""
        if suffix in {".txt", ".md", ".py"}:
            try:
                text = file_path.read_text(encoding="utf-8").strip()
            except UnicodeDecodeError:
                # Fallback for rare cases where files are saved in a legacy encoding.
                text = file_path.read_text(encoding="latin-1").strip()

            if not text:
                logging.warning("Skipping empty submission file: %s", file_path.name)
                continue

        elif suffix == ".pdf":
            text = extract_text_from_pdf(file_path)
            if not text:
                logging.warning("No text extracted from PDF submission: %s", file_path.name)
                # continue to next file (skip if extraction failed)
                continue

        elif suffix == ".docx":
            text = extract_text_from_docx(file_path)
            if not text:
                logging.warning("No text extracted from DOCX submission: %s", file_path.name)
                continue

        else:
            # .doc and other binary doc formats are not supported for extraction
            logging.warning("Skipping unsupported binary submission format: %s", file_path.name)
            continue

        student_id = file_path.stem
        submissions[student_id] = text
        logging.info("Loaded submission for student: %s", student_id)

    if not submissions:
        raise ValueError("No valid non-empty .txt/.md/.py submission files found.")

    logging.info("Completed file read. Total submissions loaded: %d", len(submissions))
    return submissions
