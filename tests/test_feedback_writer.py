import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.feedback_writer_task import feedback_writer_task
from tasks.rubric_evaluator_task import rubric_evaluator_task
from tools.feedback_tool import save_draft_feedback


def test_feedback_writer_task_wiring_and_prompt_contract():
    assert feedback_writer_task.agent is not None
    assert rubric_evaluator_task in feedback_writer_task.context

    description = feedback_writer_task.description
    assert "{rubric_evaluation_output}" in description
    assert "save_draft_feedback" in description
    assert "student_id" in description
    assert "feedback_text" in description


def test_save_draft_feedback_writes_expected_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    student_id = "STU_TEST_001"
    feedback_text = "Great effort. Improve citation quality in Research."

    message = save_draft_feedback.run(student_id=student_id, feedback_text=feedback_text)
    expected_path = Path("data/feedbacks") / f"{student_id}_draft_feedback.md"

    assert expected_path.exists()
    assert expected_path.read_text(encoding="utf-8") == feedback_text
    assert str(expected_path).replace("\\", "/") in message