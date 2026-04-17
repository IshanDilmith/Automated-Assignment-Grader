from crewai import Agent
from crewai import LLM
from tools.reporter_tool import calculate_final_grade_and_check_plagiarism

# Use a model that actually supports tools
ollama_llm = LLM(
    model="ollama/qwen2.5:7b",        # ← Change here
    base_url="http://localhost:11434",
    api_key="ollama",
    temperature=0.2                    # Lower temperature = more reliable for grading
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
        verbose=True,
        allow_delegation=False,
        max_iter=8
    )