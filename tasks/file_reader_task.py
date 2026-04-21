from crewai import Task

from agents.file_reader_agent import create_file_reader_agent


file_reader_agent = create_file_reader_agent()

file_reader_task = Task(
    description=(
        "Read all student submissions from this folder path: {submission_folder_path}.\n"
        "You must call the tool read_submission_files exactly once using the same path.\n"
        "Accepted file types: .txt, .md, .py. Ignore everything else.\n"
        "Return only the resulting dictionary where each key is student_id and each value is full submission text."
    ),
    agent=file_reader_agent,
    expected_output=(
        "A dictionary of student submissions, e.g. {'STU001': '...', 'STU002': '...'}"
    ),
)
