"""Main entrypoint for the beginner-friendly Automated Assignment Grader pipeline."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict

from crewai import Crew, Process

from agents.feedback_writer_agent import feedback_writer_agent
from agents.file_reader_agent import create_file_reader_agent
from agents.grade_reporter_agent import create_grade_reporter_agent
from agents.rubric_evaluator_agent import create_rubric_evaluator_agent
from tasks.feedback_writer_task import feedback_writer_task
from tasks.file_reader_task import file_reader_task
from tasks.grade_reporter_task import grade_reporter_task
from tasks.rubric_evaluator_task import rubric_evaluator_task
from tools.file_reader_tool import read_submission_files


def _configure_logging() -> None:
    """Set up project logging to logs/execution.log."""
    Path("logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename="logs/execution.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _create_required_folders() -> None:
    """Create folders needed for local runs."""
    Path("data/submissions").mkdir(parents=True, exist_ok=True)
    Path("data/feedbacks").mkdir(parents=True, exist_ok=True)
    Path("data/final_reports").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)


def _build_crew() -> Crew:
    """Create one sequential 4-agent Crew instance."""
    file_reader_agent = create_file_reader_agent()
    rubric_evaluator_agent = create_rubric_evaluator_agent()
    grade_reporter_agent = create_grade_reporter_agent()

    # Explicit task chain: each task sees previous output as context.
    rubric_evaluator_task.context = [file_reader_task]
    feedback_writer_task.context = [rubric_evaluator_task]
    grade_reporter_task.context = [feedback_writer_task, rubric_evaluator_task]

    return Crew(
        agents=[
            file_reader_agent,
            rubric_evaluator_agent,
            feedback_writer_agent,
            grade_reporter_agent,
        ],
        tasks=[
            file_reader_task,
            rubric_evaluator_task,
            feedback_writer_task,
            grade_reporter_task,
        ],
        process=Process.sequential,
        verbose=2,
    )


def run_grader(
    submissions_folder: str = "data/submissions",
    rubric_path: str = "data/rubric.json",
) -> Dict[str, Any]:
    """Run the full grader once per student using a sequential Crew.

    This is the simplest reliable beginner approach for multi-student grading.
    """
    _configure_logging()
    _create_required_folders()
    os.environ.setdefault("OLLAMA_MODEL", "ollama/qwen2.5:7b")

    print("=== STAGE: Load Submissions ===")
    logging.info("Loading submissions from: %s", submissions_folder)

    # Use the existing tool so file filtering behavior stays centralized.
    all_submissions = read_submission_files.run(folder_path=submissions_folder)
    if not isinstance(all_submissions, dict) or not all_submissions:
        raise ValueError("No valid submissions found to grade.")

    print(f"Loaded {len(all_submissions)} submission(s).")
    results: Dict[str, Any] = {}

    for student_id, submission_text in sorted(all_submissions.items()):
        print("\n" + "=" * 72)
        print(f"=== STUDENT: {student_id} ===")
        print("=" * 72)
        logging.info("Starting grading pipeline for student_id=%s", student_id)

        crew = _build_crew()

        print("=== STAGE: Sequential 4-Agent Pipeline ===")
        result = crew.kickoff(
            inputs={
                "submissions_folder": submissions_folder,
                "submission_folder_path": submissions_folder,
                "rubric_path": rubric_path,
                "student_id": student_id,
                "submission_text": submission_text,
                "all_submissions": all_submissions,
            }
        )

        results[student_id] = result
        logging.info("Completed grading pipeline for student_id=%s", student_id)

    print("\n" + "=" * 72)
    print("FINAL SUMMARY")
    print("=" * 72)
    print(f"Students processed: {len(results)}")

    return results


if __name__ == "__main__":
    try:
        run_grader()
    except Exception as exc:  # pragma: no cover
        _configure_logging()
        logging.exception("Grader execution failed: %s", exc)
        print("An error occurred while running the grader.")
        print(f"Details: {exc}")
