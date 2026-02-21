"""Model-based grader: evaluates scheduling helpfulness using a rubric."""

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
        name="clarity",
        description="Agent clearly explained what compliance item is missing and why it matters. 0=not mentioned, 1=mentioned but vague, 2=clearly explained.",
        max_score=2,
    ),
    RubricCriterion(
        name="options",
        description="Agent offered concrete scheduling options or next steps. 0=no options, 1=vague suggestion, 2=specific actionable options.",
        max_score=2,
    ),
    RubricCriterion(
        name="empathy",
        description="Agent showed empathy and reassurance (not punitive). 0=cold/robotic, 1=neutral, 2=warm and reassuring.",
        max_score=2,
    ),
]


class SchedulingHelpfulnessGrader(Grader):
    """Evaluates how helpfully the agent handled compliance scheduling."""

    @property
    def name(self) -> str:
        return "scheduling_helpfulness"

    @property
    def is_model_based(self) -> bool:
        return True

    def grade(self, **kwargs) -> GraderResult:
        transcript: ConversationTranscript = kwargs["transcript"]

        return evaluate_with_rubric(
            grader_name=self.name,
            transcript_text=transcript.full_text,
            context="Evaluate how the agent handled compliance gap discovery and scheduling remediation.",
            criteria=CRITERIA,
        )
