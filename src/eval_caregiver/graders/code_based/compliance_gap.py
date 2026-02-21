from __future__ import annotations

from eval_caregiver.graders.base import Grader
from eval_caregiver.schemas.caregiver import StructuredIntakeRecord
from eval_caregiver.schemas.grader_results import GraderResult
from eval_caregiver.schemas.scenarios import TestScenario


class ComplianceGapGrader(Grader):
    """Checks whether the agent identified all expected compliance gaps."""

    @property
    def name(self) -> str:
        return "compliance_gap_detection"

    def grade(self, **kwargs) -> GraderResult:
        scenario: TestScenario = kwargs["scenario"]
        intake_record: StructuredIntakeRecord = kwargs["intake_record"]

        expected = set(scenario.expected_compliance_gaps)
        found = set(intake_record.compliance_gaps)

        if not expected:
            return GraderResult(
                grader_name=self.name,
                passed=True,
                score=1.0,
                details="No compliance gaps expected; none required.",
            )

        detected = expected & found
        missed = expected - found
        recall = len(detected) / len(expected)

        passed = recall >= 0.95
        details_parts = [f"Expected: {sorted(expected)}", f"Found: {sorted(found)}"]
        if missed:
            details_parts.append(f"Missed: {sorted(missed)}")

        return GraderResult(
            grader_name=self.name,
            passed=passed,
            score=recall,
            details="; ".join(details_parts),
        )
