from __future__ import annotations

from eval_caregiver.graders.base import Grader
from eval_caregiver.schemas.caregiver import StructuredIntakeRecord
from eval_caregiver.schemas.conversation import AgentActionLog
from eval_caregiver.schemas.grader_results import GraderResult
from eval_caregiver.schemas.scenarios import TestScenario


class GeoRestrictionGrader(Grader):
    """Checks whether the agent flagged geographic over-restriction and suggested alternatives."""

    @property
    def name(self) -> str:
        return "geo_restriction_detection"

    def grade(self, **kwargs) -> GraderResult:
        scenario: TestScenario = kwargs["scenario"]
        intake_record: StructuredIntakeRecord = kwargs["intake_record"]
        action_log: AgentActionLog = kwargs["action_log"]

        expected_concerns = set(scenario.expected_geo_concerns)
        if not expected_concerns:
            return GraderResult(
                grader_name=self.name,
                passed=True,
                score=1.0,
                details="No geo concerns expected.",
            )

        found_concerns = set(intake_record.geo_concerns)
        detected = expected_concerns & found_concerns
        missed = expected_concerns - found_concerns

        concern_recall = len(detected) / len(expected_concerns) if expected_concerns else 1.0

        # Check if safe area suggestions were provided
        has_suggestions = len(intake_record.safe_area_suggestions) > 0
        consulted_map = action_log.safety_map_consulted

        # Score: 50% concern detection, 25% suggestions, 25% map consultation
        score = (concern_recall * 0.5) + (0.25 if has_suggestions else 0.0) + (0.25 if consulted_map else 0.0)
        passed = score >= 0.80

        details_parts = [f"Expected concerns: {sorted(expected_concerns)}"]
        if detected:
            details_parts.append(f"Detected: {sorted(detected)}")
        if missed:
            details_parts.append(f"Missed: {sorted(missed)}")
        if has_suggestions:
            details_parts.append(f"Safe area suggestions: {intake_record.safe_area_suggestions}")
        else:
            details_parts.append("No safe area suggestions provided")
        details_parts.append(f"Safety map consulted: {consulted_map}")

        return GraderResult(
            grader_name=self.name,
            passed=passed,
            score=score,
            details="; ".join(details_parts),
        )
