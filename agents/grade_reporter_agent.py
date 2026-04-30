import os

from crewai import Agent, LLM

from tools.reporter_tool import calculate_final_grade_and_check_plagiarism


ollama_llm = LLM(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    base_url="http://localhost:11434",
    api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
    temperature=0.2,
)


def create_grade_reporter_agent():
    return Agent(
        role="Senior Grade Reporter & Plagiarism Checker",
        goal="Calculate final grades, detect plagiarism using text similarity, and generate clean professional Markdown grading reports",
        backstory=(
            "You are the final authority in the grading pipeline. "
            "You receive rubric scores and feedback from previous agents. "
            "You must calculate the final numerical grade, perform a plagiarism check, "
            "and produce a professional report file. "
            "Always call the calculate_final_grade_and_check_plagiarism tool with the exact inputs provided."
        ),
        tools=[calculate_final_grade_and_check_plagiarism],
        llm=ollama_llm,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
    )
