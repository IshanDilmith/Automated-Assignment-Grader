from crewai import Task

from agents.rubric_evaluator_agent import create_rubric_evaluator_agent
from tasks.file_reader_task import file_reader_task


rubric_evaluator_agent = create_rubric_evaluator_agent()


rubric_evaluator_task = Task(
    description=(
        "=== STAGE: Rubric Evaluator ===\n"
        "The previous task output is provided below as context. Use it only as support data.\n"
        "You must grade the CURRENT student from direct inputs:\n"
        "- student_id: {student_id}\n"
        "- submission_text: {submission_text}\n"
        "- rubric_path: {rubric_path}\n\n"
        "RUBRIC CRITERIA & POINT ALLOCATION:\n"
        "- Content (30 points): Relevance, accuracy, depth of topic\n"
        "- Structure (25 points): Logical flow, clear intro, body, conclusion\n"
        "- Research (20 points): Evidence of research, citations, source quality\n"
        "- Writing (25 points): Grammar, clarity, professional tone, formatting\n"
        "Total: 100 points\n\n"
        "Step 1: Call the tool 'load_rubric' exactly once with rubric_path.\n"
        "Step 2: Use the loaded rubric to evaluate the submission fairly.\n"
        "Step 3: Return STRICT JSON only (no markdown, no extra text) in this structure:\n"
        "{\n"
        '  "student_id": "<id>",\n'
        '  "rubric_scores": {"Content": 0, "Structure": 0, "Research": 0, "Writing": 0},\n'
        '  "total": 0,\n'
        '  "justification": {\n'
        '    "Content": "<why this score>",\n'
        '    "Structure": "<why this score>",\n'
        '    "Research": "<why this score>",\n'
        '    "Writing": "<why this score>"\n'
        "  },\n"
        '  "rubric_source": "{rubric_path}"\n'
        "}\n"
        "Rules: total must equal the sum of rubric_scores (max 30+25+20+25=100 points)."
    ),
    expected_output=(
        "A strict JSON object with student_id, rubric_scores, total, justification, and rubric_source."
    ),
    agent=rubric_evaluator_agent,
    context=[file_reader_task],
)
