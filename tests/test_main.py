import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from crewai import Process


class DummyCrew:
    """Small test double for Crew that captures constructor args and kickoff inputs."""

    last_init_kwargs = None
    last_kickoff_inputs = None

    def __init__(self, **kwargs):
        DummyCrew.last_init_kwargs = kwargs

    def kickoff(self, inputs):
        DummyCrew.last_kickoff_inputs = inputs
        return {"status": "ok", "pipeline": "sequential"}


class _ReadSubmissionsStub:
    @staticmethod
    def run(folder_path):
        return {"STU001": "Sample submission text."}


def _mock_single_submission(monkeypatch):
    monkeypatch.setattr(main, "read_submission_files", _ReadSubmissionsStub)


def test_run_grader_builds_sequential_crew(monkeypatch):
    monkeypatch.setattr(main, "Crew", DummyCrew)
    _mock_single_submission(monkeypatch)

    result = main.run_grader(submissions_folder="data/submissions")

    assert result == {"STU001": {"status": "ok", "pipeline": "sequential"}}
    assert DummyCrew.last_init_kwargs is not None
    assert DummyCrew.last_init_kwargs["process"] == Process.sequential
    assert DummyCrew.last_init_kwargs["verbose"] == 2

    assert len(DummyCrew.last_init_kwargs["agents"]) == 4
    assert len(DummyCrew.last_init_kwargs["tasks"]) == 4


def test_run_grader_passes_expected_inputs_and_context(monkeypatch):
    monkeypatch.setattr(main, "Crew", DummyCrew)
    _mock_single_submission(monkeypatch)

    custom_folder = "data/submissions"
    main.run_grader(submissions_folder=custom_folder)

    assert DummyCrew.last_kickoff_inputs["submissions_folder"] == custom_folder
    assert DummyCrew.last_kickoff_inputs["submission_folder_path"] == custom_folder
    assert DummyCrew.last_kickoff_inputs["rubric_path"] == "data/rubric.json"
    assert DummyCrew.last_kickoff_inputs["student_id"] == "STU001"
    assert DummyCrew.last_kickoff_inputs["submission_text"] == "Sample submission text."

    # Validate explicit context chaining set in main.run_grader
    assert main.rubric_evaluator_task.context == [main.file_reader_task]
    assert main.feedback_writer_task.context == [main.rubric_evaluator_task]
    assert main.grade_reporter_task.context == [main.feedback_writer_task, main.rubric_evaluator_task]


def test_run_grader_sets_default_model_env_and_creates_log_file(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "Crew", DummyCrew)
    _mock_single_submission(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    main.run_grader()

    assert os.environ["OLLAMA_MODEL"] == "ollama/qwen2.5:7b"
    assert Path("logs/execution.log").parent.exists()
