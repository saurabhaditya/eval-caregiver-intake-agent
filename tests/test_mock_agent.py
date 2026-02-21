"""Tests for mock agent."""

import pytest

from eval_caregiver.agent.mock_agent import MockAgent
from eval_caregiver.schemas.scenarios import TestScenario


class TestMockAgent:
    def setup_method(self):
        self.agent = MockAgent()

    def _make_scenario(self, scenario_id: str) -> TestScenario:
        return TestScenario(
            scenario_id=scenario_id,
            name=f"Test {scenario_id}",
            description="Test scenario",
            collection="test",
            grader_names=[],
        )

    def test_cpr_missing_scenario(self):
        output = self.agent.run_scenario(self._make_scenario("compliance_cpr_missing"))
        assert output.transcript.scenario_id == "compliance_cpr_missing"
        assert len(output.transcript.turns) > 0
        assert "CPR Certification" in output.intake_record.compliance_gaps
        assert output.action_log.scheduling_offered is True

    def test_cpr_unknown_scenario(self):
        output = self.agent.run_scenario(self._make_scenario("compliance_cpr_unknown"))
        assert "CPR Certification" in output.intake_record.compliance_gaps

    def test_cpr_present_scenario(self):
        output = self.agent.run_scenario(self._make_scenario("compliance_cpr_present"))
        assert output.intake_record.compliance_gaps == []
        assert output.intake_record.overall_status == "complete"

    def test_geo_restricted_scenario(self):
        output = self.agent.run_scenario(self._make_scenario("geo_over_restricted"))
        assert "over_restricted_zones" in output.intake_record.geo_concerns
        assert len(output.intake_record.safe_area_suggestions) > 0
        assert output.action_log.safety_map_consulted is True

    def test_geo_no_alternatives_scenario(self):
        output = self.agent.run_scenario(self._make_scenario("geo_no_alternatives"))
        assert output.intake_record.geo_concerns == []
        assert output.intake_record.safe_area_suggestions == []
        assert output.action_log.safety_map_consulted is False

    def test_unknown_scenario_raises(self):
        with pytest.raises(ValueError, match="No response registered"):
            self.agent.run_scenario(self._make_scenario("nonexistent"))

    def test_custom_registration(self):
        from eval_caregiver.agent.base import AgentOutput
        from eval_caregiver.schemas.caregiver import CaregiverProfile, StructuredIntakeRecord
        from eval_caregiver.schemas.conversation import AgentActionLog, ConversationTranscript

        def custom_builder(sid: str) -> AgentOutput:
            return AgentOutput(
                transcript=ConversationTranscript(scenario_id=sid, turns=[]),
                intake_record=StructuredIntakeRecord(
                    caregiver=CaregiverProfile(caregiver_id="custom", full_name="Custom"),
                ),
                action_log=AgentActionLog(scenario_id=sid),
            )

        self.agent.register("custom_scenario", custom_builder)
        output = self.agent.run_scenario(self._make_scenario("custom_scenario"))
        assert output.intake_record.caregiver.caregiver_id == "custom"
