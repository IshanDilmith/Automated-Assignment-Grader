from crewai.tools import tool
import os


@tool("save_draft_feedback")
def save_draft_feedback(student_id: str, feedback_text: str) -> str:
    """
    Saves the draft feedback as a markdown file and returns the full file path.
    
    Args:
        student_id (str): Student identifier (e.g., "student_001" or "Ishan Dilmith").
        feedback_text (str): The complete feedback text written by the agent.
    
    Returns:
        str: Confirmation message with the exact path where the file was saved.
    """
    # Create folder if it doesn't exist
    output_dir = "data/feedbacks"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as markdown file
    file_path = f"{output_dir}/{student_id}_draft_feedback.md"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(feedback_text)
    
    return f"Draft feedback successfully saved to: {file_path}"