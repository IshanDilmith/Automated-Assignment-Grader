from crewai import Task

from agents.grade_reporter_agent import create_grade_reporter_agent
from tasks.feedback_writer_task import feedback_writer_task
from tasks.rubric_evaluator_task import rubric_evaluator_task


grade_reporter_agent = create_grade_reporter_agent()


grade_reporter_task = Task(
    description=(
        "=== STAGE: Grade Reporter ===\n"
        "The previous task output is provided below as context.\n"
        "Extract these fields from context and current inputs:\n"
        "- student_id\n"
        "- submission_text\n"
        "- rubric_scores (from rubric evaluator JSON)\n"
        "- feedback_text (from feedback writer JSON)\n"
        "- all_submissions (from kickoff input)\n\n"
        "Call tool 'calculate_final_grade_and_check_plagiarism' exactly once with those values.\n"
        "Return STRICT JSON only:\n"
        "{\n"
        '  "student_id": "<id>",\n'
        '  "final_grade": 0,\n'
        '  "avg_plagiarism": 0,\n'
        '  "report_path": "data/final_reports/<id>_final_report.md",\n'
        '  "status": "completed|failed"\n'
        "}"
    ),
    expected_output=(
        "A strict JSON object with student_id, final_grade, avg_plagiarism, report_path, and status."
    ),
    agent=grade_reporter_agent,
    context=[feedback_writer_task, rubric_evaluator_task],
)
