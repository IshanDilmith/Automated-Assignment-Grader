from crewai import Agent, LLM

from tools.file_reader_tool import read_submission_files


# local Ollama configuration pattern
ollama_llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    api_key="ollama",
    temperature=0.1,
)


def create_file_reader_agent() -> Agent:
    """Create the File Reader Agent for loading student submissions into shared state."""
    return Agent(
        role="Precise File Reading Specialist",
        goal="Read all student submission files accurately and return clean structured data for downstream agents.",
        backstory=(
            "You are a careful academic operations assistant. "
            "You only read files that exist in the submissions folder and never invent content. "
            "You always use the read_submission_files tool to gather data and return it in a clean dictionary format."
        ),
        tools=[read_submission_files],
        llm=ollama_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )
