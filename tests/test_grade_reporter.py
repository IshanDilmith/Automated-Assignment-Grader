from agents.grade_reporter_agent import create_grade_reporter_agent
from crewai import Task, Crew
import json

def test_my_agent():
    # High-quality sample data that previous agents would provide
    sample_input = {
        "student_id": "STU001",
        "submission_text": """Machine learning is a branch of artificial intelligence that enables computers 
to learn from data without being explicitly programmed. It has many applications in education, 
such as personalized learning systems, automated grading, and student performance prediction.""",
        "rubric_scores": {
            "Content": 28,
            "Structure": 22,
            "Research": 18,
            "Writing": 15
        },
        "feedback_text": "Excellent research but needs better structure in the conclusion.",
        "all_submissions": {
            "STU001": """Machine learning is a branch of artificial intelligence that enables computers 
to learn from data without being explicitly programmed. It has many applications in education, 
such as personalized learning systems, automated grading, and student performance prediction.""",
            "STU002": "Machine learning is a subset of artificial intelligence and has many uses in modern technology.",
            "STU003": "Climate change is one of the most pressing environmental issues facing the world today."
        }
    }

    # Create the agent
    agent = create_grade_reporter_agent()

    # Clear and detailed task description - This is the most important improvement
    task = Task(
        description=(
            f"You are the Senior Grade Reporter & Plagiarism Checker. "
            f"Process this student submission and produce the final grading report.\n\n"
            f"Student ID: {sample_input['student_id']}\n\n"
            f"Submission Text (this is the actual student assignment):\n"
            f"{sample_input['submission_text']}\n\n"
            f"Rubric Scores received from Rubric Evaluator:\n"
            f"{json.dumps(sample_input['rubric_scores'], indent=2)}\n\n"
            f"Feedback received from Feedback Writer:\n"
            f"{sample_input['feedback_text']}\n\n"
            f"All Submissions for Plagiarism Check (dictionary):\n"
            f"{json.dumps(sample_input['all_submissions'], indent=2)}\n\n"
            "Important Instructions:\n"
            "1. Use the tool 'calculate_final_grade_and_check_plagiarism' exactly once.\n"
            "2. Pass ALL five arguments correctly: student_id, submission_text, rubric_scores, feedback_text, all_submissions.\n"
            "3. Do not mix up submission_text with feedback_text.\n"
            "4. After calling the tool, summarize the final grade and plagiarism result."
        ),
        expected_output=(
            "A complete final grading report saved as Markdown file in data/final_reports/ folder, "
            "along with a dictionary containing final_grade, avg_plagiarism, and report_path."
        ),
        agent=agent
    )

    # Create and run the crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        process="sequential"
    )

    print("🚀 Starting Grade Reporter Agent Test...")
    result = crew.kickoff()
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    if isinstance(result, dict):
        print("Final Result Keys:", list(result.keys()))
    else:
        print("Final Result:", result)
    
    print(f"\n📁 Check the report here: data/final_reports/{sample_input['student_id']}_final_report.md")

if __name__ == "__main__":
    test_my_agent()