from crewai import Agent
from tools.feedback_tool import save_draft_feedback

# Feedback Writer Agent
feedback_writer_agent = Agent(
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
    llm="ollama/qwen2.5:7b",           # change only if team uses a different model
    tools=[save_draft_feedback],      # custom tool
    verbose=True,                     # shows thinking + tool calls (great for observability)
    allow_delegation=False,
    max_iter=5
)