from __future__ import annotations

from pydantic import BaseModel, Field


class RubricCriterionScore(BaseModel):
    """Score for a single rubric criterion in a model-based grader."""

    criterion: str = Field(description="Name of the criterion being scored")
    score: int = Field(description="Score value (typically 0-2)")
    max_score: int = Field(default=2, description="Maximum possible score for this criterion")
    rationale: str = Field(default="", description="Explanation for the score")


class GraderResult(BaseModel):
    """Result from a single grader evaluation."""

    grader_name: str = Field(description="Name of the grader that produced this result")
    passed: bool = Field(description="Whether the grader check passed")
    score: float = Field(description="Numeric score (0.0 to 1.0)")
    details: str = Field(default="", description="Human-readable details about the result")
    criterion_scores: list[RubricCriterionScore] = Field(
        default_factory=list, description="Per-criterion scores (for rubric-based graders)"
    )


class ScenarioResult(BaseModel):
    """Aggregated result for a single test scenario."""

    scenario_id: str = Field(description="ID of the scenario that was evaluated")
    scenario_name: str = Field(description="Human-readable name of the scenario")
    grader_results: list[GraderResult] = Field(default_factory=list, description="Results from all graders")
    passed: bool = Field(default=False, description="Whether all required graders passed")
    needs_manual_review: bool = Field(default=False, description="Whether manual review is recommended")
    review_reasons: list[str] = Field(
        default_factory=list, description="Reasons manual review was flagged"
    )

    @property
    def overall_score(self) -> float:
        """Average score across all graders."""
        if not self.grader_results:
            return 0.0
        return sum(r.score for r in self.grader_results) / len(self.grader_results)
