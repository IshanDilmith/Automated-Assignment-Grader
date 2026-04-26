"""Main entrypoint for the beginner-friendly Automated Assignment Grader pipeline."""

from __future__ import annotations

import logging
import os
import json
import re
from pathlib import Path
from typing import Any, Dict
from urllib import error, request

import sys

# Ensure stdout/stderr use UTF-8 on Windows consoles to avoid "charmap" encoding errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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


def _ollama_preflight() -> None:
    """Confirm Ollama responds before the crew starts."""
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    print("=== STAGE: Ollama Preflight ===")
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,
            "options": {"num_predict": 8},
        }
    ).encode("utf-8")

    req = request.Request(
        "http://localhost:11434/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["choices"][0]["message"]["content"]
            print(f"Preflight OK: {text[:120]}")
            logging.info("Ollama preflight succeeded for model=%s", model)
    except error.URLError as exc:
        logging.exception("Ollama preflight failed: %s", exc)
        raise RuntimeError(f"Ollama preflight failed: {exc}") from exc


def _call_chat(messages: list[dict[str, str]], timeout: int = 120) -> str:
    import time as _time
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": 0.1,
            "options": {"num_predict": 2048},
        }
    ).encode("utf-8")
    req = request.Request(
        "http://localhost:11434/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print(f"  [LLM] Sending request to {model} ...", flush=True)
    start = _time.time()
    with request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed = _time.time() - start
    print(f"  [LLM] Response received in {elapsed:.1f}s", flush=True)
    return str(data["choices"][0]["message"]["content"])


def _extract_json_block(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}

    try:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return {}
    return {}


def _bounded_int(value: Any, minimum: int, maximum: int) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return minimum
    return max(minimum, min(maximum, number))


def _grade_student_direct(
    student_id: str,
    submission_text: str,
    rubric_path: str,
    all_submissions: dict[str, str],
) -> dict[str, Any]:
    """Grade a single student using the direct (non-CrewAI) pipeline.

    Executes the 4-task grading pipeline in order:
      1. File Reader Task   – Already done: submission_text is passed in from run_grader()
      2. Rubric Evaluator   – LLM grades the submission against the rubric (scores + feedback)
      3. Feedback Writer    – Saves the draft feedback markdown to data/feedbacks/
      4. Grade Reporter     – Calculates final grade, runs plagiarism check, saves report
    """
    from tools.feedback_tool import save_draft_feedback
    from tools.reporter_tool import calculate_final_grade_and_check_plagiarism

    rubric_raw = Path(rubric_path).read_text(encoding="utf-8")
    rubric = json.loads(rubric_raw)
    criteria = rubric.get("criteria", {})

    if not isinstance(criteria, dict) or not criteria:
        criteria = {
            "Content": {"max_points": 30},
            "Structure": {"max_points": 25},
            "Research": {"max_points": 20},
            "Writing": {"max_points": 25},
        }

    # Build the expected keys from the rubric so the prompt exactly matches
    score_keys = list(criteria.keys())
    score_template = {k: 0 for k in score_keys}

    system_prompt = (
        "You are a strict academic grader. "
        "Return ONLY valid JSON with keys: rubric_scores, feedback_markdown. "
        "No extra text before or after the JSON."
    )
    user_prompt = (
        f"Student ID: {student_id}\n\n"
        f"Rubric JSON:\n{json.dumps(rubric, ensure_ascii=False)}\n\n"
        f"Submission:\n{submission_text}\n\n"
        "Return JSON in this exact shape:\n"
        "{\n"
        f'  "rubric_scores": {json.dumps(score_template)},\n'
        '  "feedback_markdown": "criterion-by-criterion feedback with clear suggestions"\n'
        "}\n"
    )

    # TASK 2: Rubric Evaluator – LLM scores the submission per rubric
    print(f"  → Step 1/3: Grading against rubric ...", flush=True)
    model_text = _call_chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        timeout=150,
    )
    parsed = _extract_json_block(model_text)
    raw_scores = parsed.get("rubric_scores", {})

    scores: dict[str, int] = {}
    for key, config in criteria.items():
        max_points = 100
        if isinstance(config, dict):
            max_points = int(config.get("max_points") or config.get("maxPoints") or max_points)
        scores[key] = _bounded_int(raw_scores.get(key), 0, max_points)

    feedback_markdown = str(parsed.get("feedback_markdown", "")).strip()
    if not feedback_markdown:
        feedback_markdown = "Feedback generation returned empty content. Please review submission manually."

    # TASK 3: Feedback Writer – Saves draft feedback to disk
    print(f"  → Step 2/3: Saving feedback ...", flush=True)
    save_draft_feedback.run(student_id=student_id, feedback_text=feedback_markdown)

    # TASK 4: Grade Reporter – Final grade + plagiarism check + report
    print(f"  → Step 3/3: Computing final grade & plagiarism check ...", flush=True)
    report = calculate_final_grade_and_check_plagiarism.run(
        student_id=student_id,
        submission_text=submission_text,
        rubric_scores=scores,
        feedback_text=feedback_markdown,
        all_submissions=all_submissions,
    )
    print(f"  ✓ Student {student_id} grading complete.", flush=True)
    return report if isinstance(report, dict) else {"student_id": student_id, "status": "failed"}


def _build_crew() -> "Crew":
    """Create one sequential 4-agent Crew instance."""
    from crewai import Crew, Process
    from agents.feedback_writer_agent import feedback_writer_agent
    from agents.file_reader_agent import create_file_reader_agent
    from agents.grade_reporter_agent import create_grade_reporter_agent
    from agents.rubric_evaluator_agent import create_rubric_evaluator_agent
    from tasks.feedback_writer_task import feedback_writer_task
    from tasks.file_reader_task import file_reader_task
    from tasks.grade_reporter_task import grade_reporter_task
    from tasks.rubric_evaluator_task import rubric_evaluator_task

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
        verbose=False,
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
    os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:7b")
    _ollama_preflight()
    use_crewai = os.environ.get("AAG_USE_CREWAI", "0").strip().lower() in {"1", "true", "yes"}

    print("=== STAGE: Load Submissions ===")
    logging.info("Loading submissions from: %s", submissions_folder)

    # TASK 1: File Reader – Read all submission files from the folder
    # Uses tools/file_reader_tool.py → returns {student_id: text} dict
    from tools.file_reader_tool import read_submission_files

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

        try:
            if use_crewai:
                # CrewAI mode: all 4 tasks run sequentially via the Crew orchestrator
                # 1. File Reader → 2. Rubric Evaluator → 3. Feedback Writer → 4. Grade Reporter
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
            else:
                # Direct mode: tasks 2-4 run in _grade_student_direct()
                # (Task 1 already done above by read_submission_files)
                # 2. Rubric Evaluator → 3. Feedback Writer → 4. Grade Reporter
                print("=== STAGE: Direct Grading Pipeline ===")
                result = _grade_student_direct(
                    student_id=student_id,
                    submission_text=submission_text,
                    rubric_path=rubric_path,
                    all_submissions=all_submissions,
                )

            results[student_id] = result
            logging.info("Completed grading pipeline for student_id=%s", student_id)
        except Exception as exc:
            logging.exception("Failed grading pipeline for student_id=%s: %s", student_id, exc)
            results[student_id] = {"student_id": student_id, "status": "failed", "error": str(exc)}
            print(f"Student {student_id} failed: {exc}")

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
