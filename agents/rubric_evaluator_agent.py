import os
from crewai import Agent, LLM
from tools.rubric_tool import load_rubric
from tools.justification_tool import save_rubric_justification

# local Ollama configuration pattern
ollama_llm = LLM(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    base_url="http://localhost:11434",
    api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
    temperature=0.2,
)

def create_rubric_evaluator_agent() -> Agent:
    """Create the Rubric Evaluator Agent for analyzing student submissions."""
    return Agent(
        role="Academic Rubric Evaluator",
        goal="Objectively evaluate student submissions against a specific rubric and assign accurate marks.",
        backstory=(
            "You are a rigorous academic evaluator with years of experience in grading assignments. "
            "You are known for your fairness and attention to detail. "
            "You analyze submissions based on content, structure, research quality, and writing clarity. "
            "You always provide a justification for the marks you assign and never deviate from the provided rubric."
        ),
        tools=[load_rubric, save_rubric_justification],
        llm=ollama_llm,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
    )
