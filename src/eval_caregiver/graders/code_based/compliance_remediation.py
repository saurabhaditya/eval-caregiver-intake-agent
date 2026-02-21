from __future__ import annotations

from eval_caregiver.graders.base import Grader
from eval_caregiver.schemas.caregiver import StructuredIntakeRecord
from eval_caregiver.schemas.conversation import AgentActionLog
from eval_caregiver.schemas.grader_results import GraderResult
from eval_caregiver.schemas.scenarios import TestScenario


class ComplianceRemediationGrader(Grader):
    """Checks whether the agent offered remediation for identified compliance gaps."""

    @property
    def name(self) -> str:
        return "compliance_remediation"

    def grade(self, **kwargs) -> GraderResult:
        scenario: TestScenario = kwargs["scenario"]
        intake_record: StructuredIntakeRecord = kwargs["intake_record"]
        action_log: AgentActionLog = kwargs["action_log"]

        expected_gaps = set(scenario.expected_compliance_gaps)
        if not expected_gaps:
            return GraderResult(
                grader_name=self.name,
                passed=True,
                score=1.0,
                details="No compliance gaps expected; remediation not required.",
            )

        # Check that remediation actions were offered
        has_remediation_actions = len(intake_record.remediation_actions) > 0
        has_scheduling = action_log.scheduling_offered
        has_remediation_steps = len(action_log.remediation_steps_offered) > 0

        signals = [has_remediation_actions, has_scheduling, has_remediation_steps]
        score = sum(signals) / len(signals)
        passed = score >= 0.85

        details_parts = []
        if has_remediation_actions:
            details_parts.append(f"Remediation actions: {intake_record.remediation_actions}")
        else:
            details_parts.append("No remediation actions in intake record")
        if has_scheduling:
            details_parts.append("Scheduling was offered")
        else:
            details_parts.append("Scheduling was NOT offered")
        if has_remediation_steps:
            details_parts.append(f"Remediation steps: {action_log.remediation_steps_offered}")
        else:
            details_parts.append("No remediation steps offered")

        return GraderResult(
            grader_name=self.name,
            passed=passed,
            score=score,
            details="; ".join(details_parts),
        )
