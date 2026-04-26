from pydantic import BaseModel
from typing import Dict


class RubricScores(BaseModel):
    Content: int
    Structure: int
    Research: int
    Writing: int


class RubricEvaluatorOutput(BaseModel):
    student_id: str
    rubric_scores: RubricScores
    total: int
    justification: Dict[str, str]
    rubric_source: str


class CriterionFeedback(BaseModel):
    reason: str
    suggestion: str


class FeedbackWriterOutput(BaseModel):
    student_id: str
    criterion_feedback: Dict[str, CriterionFeedback]
    feedback_text: str
    tool_status: str


class GradeReporterOutput(BaseModel):
    student_id: str
    final_grade: float
    avg_plagiarism: float
    report_path: str
    status: str
