import logging
from pathlib import Path
from datetime import datetime
import json

from crewai.tools import tool

# Logging for observability
logging.basicConfig(
    filename='logs/execution.log',
    level=logging.INFO,
    format='%(asctime)s - GRADE_REPORTER_TOOL - %(levelname)s - %(message)s'
)

@tool("calculate_final_grade_and_check_plagiarism")
def calculate_final_grade_and_check_plagiarism(
    student_id: str,
    submission_text: str,
    rubric_scores: dict,
    feedback_text: str,
    all_submissions: dict | list,
    justification: dict = None
) -> dict:
    """
    Final tool for Grade Reporter Agent.
    Calculates grade, checks plagiarism, and saves Markdown report.
    """
    logging.info(f"Processing final grade for student: {student_id}")

    try:
        # 1. Calculate final grade
        if not isinstance(rubric_scores, dict):
            rubric_scores = {}
        total_score = sum(rubric_scores.values())
        final_grade = round((total_score / 100) * 100, 1)

        # 2. Handle all_submissions (LLM sometimes sends list)
        if isinstance(all_submissions, list):
            logging.warning("all_submissions received as list → converting")
            all_submissions = {sid: "" for sid in all_submissions}
        if not isinstance(all_submissions, dict):
            all_submissions = {}

        # 3. Plagiarism check
        plagiarism_details = {}
        avg_plagiarism = 0.0

        if submission_text and submission_text.strip() and isinstance(all_submissions, dict) and len(all_submissions) > 1:
            try:
                from difflib import SequenceMatcher
                total_ratio = 0.0
                comparisons = 0

                for other_id, other_text in all_submissions.items():
                    # Skip self-comparison
                    if other_id == student_id:
                        continue
                    
                    if not other_text or not other_text.strip():
                        plagiarism_details[other_id] = 0.0
                        continue
                        
                    ratio = SequenceMatcher(None, submission_text, other_text).ratio()
                    score = round(ratio * 100, 1)
                    plagiarism_details[other_id] = score
                    total_ratio += score
                    comparisons += 1

                if comparisons > 0:
                    avg_plagiarism = round(total_ratio / comparisons, 1)
            except Exception as e:
                logging.error(f"Plagiarism calculation error: {e}")

        # Update return dict key name for clarity if needed, but keeping plagiarism_scores for backward compatibility in report content
        plagiarism_scores = plagiarism_details

        # 4. Create report
        justification_block = ""
        if justification:
            justification_block = f"## Score Justification:\n{json.dumps(justification, indent=2)}\n\n"

        report_content = f"""# FINAL GRADING REPORT - {student_id}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Final Grade: {final_grade}/100

## Rubric Breakdown:
{json.dumps(rubric_scores, indent=2)}

{justification_block}## Plagiarism Analysis:
Average similarity: {avg_plagiarism}%
Detailed comparison:
{json.dumps(plagiarism_scores, indent=2)}

## Teacher Feedback:
{feedback_text}

## Recommendation:
{'⚠️ HIGH PLAGIARISM DETECTED - Please investigate' if avg_plagiarism > 30 
 else '✅ Original work detected'}

---

Report generated automatically by Grade Reporter Agent.
"""

        # 5. Save file
        output_dir = Path("data/final_reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{student_id}_final_report.md"
        report_path.write_text(report_content, encoding="utf-8")

        logging.info(f"Report saved for {student_id} → Grade: {final_grade} | Plagiarism: {avg_plagiarism}%")

        return {
            "student_id": student_id,
            "final_grade": final_grade,
            "rubric_scores": rubric_scores,
            "justification": justification,
            "avg_plagiarism": avg_plagiarism,
            "plagiarism_details": plagiarism_scores,
            "report_path": str(report_path),
            "status": "completed"
        }

    except Exception as e:
        logging.error(f"Tool error for {student_id}: {e}")
        return {"student_id": student_id, "status": "failed", "error": str(e)}