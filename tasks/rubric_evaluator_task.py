from crewai import Task
from agents.rubric_evaluator_agent import create_rubric_evaluator_agent

# Create the agent instance
rubric_evaluator_agent = create_rubric_evaluator_agent()

rubric_evaluator_task = Task(
    description=(
        "Evaluate the student submission for Student ID: {student_id}.\n"
        "Submission Content:\n"
        "--- START SUBMISSION ---\n"
        "{submission_text}\n"
        "--- END SUBMISSION ---\n\n"
        "Use the following rubric to assign marks (out of 100 total):\n"
        "1. Content (30 marks): Relevance, accuracy, and depth of the topic.\n"
        "2. Structure (25 marks): Logical flow, clear introduction, body, and conclusion.\n"
        "3. Research (20 marks): Evidence of research, citations, and source quality.\n"
        "4. Writing (25 marks): Grammar, clarity, professional tone, and formatting.\n\n"
        "You must output the evaluation in the following format:\n"
        "Student ID: [ID]\n"
        "Rubric Scores:\n"
        "- Content (30 marks): [Score]/30\n"
        "- Structure (25 marks): [Score]/25\n"
        "- Research (20 marks): [Score]/20\n"
        "- Writing (25 marks): [Score]/25\n"
        "Total: [Total]/100\n\n"
        "Justification:\n"
        "[Brief paragraph explaining the scores for each criterion]\n\n"
        "JSON_SCORES: "
        '{{"Content": [Score], "Structure": [Score], "Research": [Score], "Writing": [Score]}}'
    ),
    expected_output=(
        "A detailed evaluation report containing student ID, marks for each criterion, "
        "a justification for the marks, and a JSON string of the scores."
    ),
    agent=rubric_evaluator_agent,
)
