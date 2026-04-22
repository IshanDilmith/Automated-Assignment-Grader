from crewai import Agent, LLM

# Use the same configuration as other agents in the project
ollama_llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    api_key="ollama",
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
        llm=ollama_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )
