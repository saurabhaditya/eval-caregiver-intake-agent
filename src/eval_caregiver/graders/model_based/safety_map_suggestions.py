"""Model-based grader: evaluates quality of safety map usage and area suggestions."""

from __future__ import annotations

from eval_caregiver.graders.base import Grader
from eval_caregiver.graders.model_based.llm_judge import (
    RubricCriterion,
    evaluate_with_rubric,
)
from eval_caregiver.schemas.conversation import ConversationTranscript
from eval_caregiver.schemas.grader_results import GraderResult

CRITERIA = [
    RubricCriterion(
        name="map_referenced",
        description="Agent referenced the safety map or safety data when discussing zones. 0=no reference, 1=implied, 2=explicitly referenced.",
        max_score=2,
    ),
    RubricCriterion(
        name="nearby_safe_areas",
        description="Agent identified and suggested nearby safe areas with specific details. 0=no suggestions, 1=vague suggestions, 2=specific zones with risk levels.",
        max_score=2,
    ),
    RubricCriterion(
        name="next_step",
        description="Agent provided a clear next step (e.g., revisit preferences, try a zone). 0=no next step, 1=vague, 2=specific actionable next step.",
        max_score=2,
    ),
]


class SafetyMapSuggestionsGrader(Grader):
    """Evaluates the quality of safety map consultation and area suggestions."""

    @property
    def name(self) -> str:
        return "safe_area_suggestion_quality"

    @property
    def is_model_based(self) -> bool:
        return True

    def grade(self, **kwargs) -> GraderResult:
        transcript: ConversationTranscript = kwargs["transcript"]

        return evaluate_with_rubric(
            grader_name=self.name,
            transcript_text=transcript.full_text,
            context="Evaluate how the agent used safety map data to suggest alternative geographic areas to an over-restricted caregiver.",
            criteria=CRITERIA,
        )
