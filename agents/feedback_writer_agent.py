import os

from crewai import Agent, LLM
from tools.feedback_tool import save_draft_feedback

# local Ollama configuration pattern
ollama_llm = LLM(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    base_url="http://localhost:11434",
    api_key="ollama",
    temperature=0.2,
)


def create_feedback_writer_agent() -> Agent:
    """Create the Feedback Writer Agent for rubric-based constructive feedback."""
    return Agent(
        role="Helpful Teaching Assistant",
        goal=(
            "Write clear, polite, and highly specific constructive feedback "
            "for each rubric criterion based on the scores given by the Rubric Evaluator."
        ),
        backstory=(
            "You are an experienced teaching assistant who always explains why a student "
            "received a particular score and gives friendly, actionable advice on how to improve. "
            "You never invent marks. You only use the scores and rubric provided."
        ),
        llm=ollama_llm,
        tools=[save_draft_feedback],
        verbose=False,
        allow_delegation=False,
        max_iter=2,
    )


# Backward-compatible instance used by existing task imports.
feedback_writer_agent = create_feedback_writer_agent()
