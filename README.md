# Automated Assignment Grader

A lightweight Python framework for generating assignment feedback, evaluating
submissions against a rubric, and producing final grading reports. The project
is organized around small, testable agents, tasks, and tools so components are
easy to extend or reuse.

Key features
- Generate draft feedback and finalize reports
- Evaluate submissions against a JSON rubric
- Simple, testable agent/task/tool structure

Prerequisites
- Python 3.9+ (3.12 recommended)
- pip
- Optional: Ollama (for local LLMs) if you want to run models locally

Quick start
1. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) If using Ollama, pull the desired model locally. Example:

```bash
ollama pull qwen2.5:7b
```

Running the project
- Run the main entrypoint:

```bash
python main.py
```

- Individual tasks and agents can be exercised via the `tasks/` and `agents/`
	modules for development and testing.

Project layout
- `main.py` — project entrypoint
- `agents/` — agent implementations (feedback writer, rubric evaluator, etc.)
- `tasks/` — task definitions and wiring
- `tools/` — helper utilities (file IO, reporting, rubric helpers)
- `data/` — sample data, rubrics, submissions, and generated reports
- `tests/` — unit tests

Testing
- Run unit tests with `pytest`:

```bash
python -m pytest
```

Contributing
- Feel free to open issues or PRs. Follow the existing test patterns in
	`tests/` when adding features.

License
- See the repository license or add one as appropriate for your project.

If you'd like, I can also add a short example showing how to run a specific
agent (for example `feedback_writer_agent`) or update `requirements.txt`.