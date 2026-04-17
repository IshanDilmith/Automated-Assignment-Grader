from crewai import Task
from agents.feedback_writer_agent import feedback_writer_agent


feedback_writer_task = Task(
    description=(
        "You are now receiving the complete output from the Rubric Evaluator Agent.\n"
        "Here is the rubric evaluation and scores:\n"
        "{rubric_evaluation_output}\n\n"
        
        "Using ONLY the scores and rubric above, write clear, polite, and highly specific "
        "constructive feedback for EACH rubric criterion.\n"
        "For every criterion explain:\n"
        "1. Why the student got that score\n"
        "2. One actionable suggestion for improvement\n\n"
        
        "At the VERY END you MUST call the tool 'save_draft_feedback' with:\n"
        "- student_id = the student ID from the rubric evaluation\n"
        "- feedback_text = the complete feedback you just wrote\n"
        "Do not say anything after calling the tool."
    ),
    agent=feedback_writer_agent,
    # context=[rubric_evaluator_task],
    expected_output=(
        "A polite, specific feedback text (one paragraph per criterion) "
        "plus a tool confirmation message that the draft was saved."
    )
)