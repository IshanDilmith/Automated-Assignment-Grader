import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tasks.rubric_evaluator_task import rubric_evaluator_task
from crewai import Crew

def test_rubric_evaluator():
    # Sample input data
    sample_input = {
        "student_id": "STU_METHZO",
        "submission_text": """
        # Assignment: Introduction to AI
        Artificial Intelligence (AI) is a field of computer science that focuses on creating systems 
        capable of performing tasks that typically require human intelligence. This includes learning, 
        reasoning, problem-solving, and perception. Modern AI applications range from virtual assistants 
        like Siri to self-driving cars.
        
        The research shows that deep learning, a subset of machine learning, has revolutionized image 
        recognition and natural language processing. (Source: Smith, 2023).
        
        In conclusion, AI is a rapidly evolving field with significant impacts on society.
        """
    }

    print(f"Running Rubric Evaluator Agent Test for Student: {sample_input['student_id']}...\n")

    # Replace placeholders in task description
    # This imitates how crewai handles inputs when part of a crew with interpolated strings
    # But for a solo test, we manually replace or just pass as inputs if using kickoff
    
    # Create a crew to run the single task
    crew = Crew(
        agents=[rubric_evaluator_task.agent],
        tasks=[rubric_evaluator_task],
        verbose=True
    )

    # Kickoff with inputs
    result = crew.kickoff(inputs=sample_input)

    print("\n=== FINAL EVALUATION RESULT ===")
    print(result)

if __name__ == "__main__":
    test_rubric_evaluator()
