from tasks.feedback_writer_task import feedback_writer_task
import os

# Mock data from Rubric Evaluator
mock_rubric_output = """
Student ID: Ishan_Dilmith
Rubric Scores:
- Content (10 marks): 8/10
- Structure (10 marks): 7/10
- Clarity & Language (10 marks): 9/10
Total: 24/30

Rubric used:
- Content: Depth of research, accuracy, relevance
- Structure: Logical flow, introduction & conclusion
- Clarity & Language: Clear writing, grammar, academic tone
"""

if __name__ == "__main__":
    # Replace placeholder with real mock data
    feedback_writer_task.description = feedback_writer_task.description.replace(
        "{rubric_evaluation_output}", mock_rubric_output
    )
    
    print("Running YOUR Feedback Writer Agent + Tool (solo test)...\n")
    result = feedback_writer_task.execute()
    
    print("\n=== FINAL RESULT FROM YOUR AGENT ===")
    print(result)
    
    # Check if the file was created
    feedback_file = "data/feedbacks/Ishan_Dilmith_draft_feedback.md"
    if os.path.exists(feedback_file):
        print(f"\nSUCCESS! Feedback file created → {feedback_file}")
        print("Open the file to see the feedback your agent wrote!")
    else:
        print("\nFile was not created. Check the output above.")