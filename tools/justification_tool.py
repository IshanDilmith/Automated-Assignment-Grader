from crewai.tools import tool
import os
import json

@tool("save_rubric_justification")
def save_rubric_justification(student_id: str, justification: dict) -> str:
    """
    Saves the rubric score justification as a markdown file and returns the full file path.
    
    Args:
        student_id (str): Student identifier.
        justification (dict): The justification dictionary with criterion names as keys and explanations as values.
    
    Returns:
        str: Confirmation message with the exact path where the file was saved.
    """
    # Create folder if it doesn't exist
    output_dir = "data/justifications"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as markdown file
    file_path = f"{output_dir}/{student_id}_justification.md"
    
    content = "# RUBRIC SCORE JUSTIFICATION\n\n"
    if isinstance(justification, dict):
        for criterion, explanation in justification.items():
            content += f"## {criterion}\n{explanation}\n\n"
    else:
        content += str(justification)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"Justification successfully saved to: {file_path}"
