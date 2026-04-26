from crewai import Task

from agents.feedback_writer_agent import feedback_writer_agent
from tasks.rubric_evaluator_task import rubric_evaluator_task


feedback_writer_task = Task(
    description=(
        "=== STAGE: Feedback Writer ===\n"
        "The previous task output is provided below as context.\n"
        "Extract student_id and rubric_scores from that context JSON.\n"
        "Write criterion-by-criterion feedback using only those scores.\n\n"
        "For each criterion (Content, Structure, Research, Writing), provide:\n"
        "- reason: why this score was given\n"
        "- suggestion: one actionable improvement\n\n"
        "Build one combined markdown feedback text, then call the tool 'save_draft_feedback' exactly once with:\n"
        "- student_id\n"
        "- feedback_text (the full combined markdown text)\n\n"
        "Return STRICT JSON only in this structure:\n"
        "{\n"
        '  "student_id": "<id>",\n'
        '  "criterion_feedback": {\n'
        '    "Content": {"reason": "...", "suggestion": "..."},\n'
        '    "Structure": {"reason": "...", "suggestion": "..."},\n'
        '    "Research": {"reason": "...", "suggestion": "..."},\n'
        '    "Writing": {"reason": "...", "suggestion": "..."}\n'
        "  },\n"
        '  "feedback_text": "<full markdown feedback>",\n'
        '  "tool_status": "<confirmation message from save_draft_feedback>"\n'
        "}"
    ),
    agent=feedback_writer_agent,
    context=[rubric_evaluator_task],
    expected_output=(
        "A strict JSON object with student_id, criterion_feedback, feedback_text, and tool_status."
    ),
    output_json=True,
)
