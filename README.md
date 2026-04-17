# Automated Assignment Grader

## Project Info
Automated Assignment Grader is a Python project that uses agent/task/tool modules
to generate assignment feedback and support grading workflows, including plagiarism
similarity support.

## Prerequisites
- Python 3.9+ (Recommended Python 3.12.x)
- `pip`
- [Ollama](https://ollama.com/) installed and running locally

After installing Ollama, pull a model:

```bash
ollama pull llama3:8b
```

If you have less RAM, you can use:

```bash
ollama pull phi3:medium
```

## Install Dependencies
From the project root, install packages:

```bash
pip install crewai langchain-community ollama
pip install pandas numpy scikit-learn
```

## Run Tests
You can run the feedback writer test with:

```bash
python tests/test_feedback_writer.py
```

Or run all tests (if `pytest` is installed):

```bash
python -m pytest tests
```

## Project Structure
- `main.py`: Entrypoint script.
- `agents/`: Agent implementations.
- `tasks/`: Task definitions.
- `tools/`: Supporting tools/utilities.
- `tests/`: Test files.
- `data/feedbacks/`: Output/sample feedback files.
- `logs/`: Log artifacts.