"""Tests for mock agent JSON response loading and data integrity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval_caregiver.agent.base import AgentOutput
from eval_caregiver.agent.mock_agent import MockAgent, _DATA_DIR, _LOADED_RESPONSES
from eval_caregiver.schemas.caregiver import StructuredIntakeRecord
from eval_caregiver.schemas.conversation import AgentActionLog, ConversationTranscript
from eval_caregiver.schemas.scenarios import TestScenario


def _make_scenario(scenario_id: str) -> TestScenario:
    return TestScenario(
        scenario_id=scenario_id,
        name=f"Test {scenario_id}",
        description="Test scenario",
        collection="test",
        grader_names=[],
    )


class TestResponseLoading:
    """Verify responses are loaded correctly from JSON."""

    def test_loaded_responses_not_empty(self):
        assert len(_LOADED_RESPONSES) >= 5

    def test_all_responses_are_agent_output(self):
        for scenario_id, output in _LOADED_RESPONSES.items():
            assert isinstance(output, AgentOutput), f"{scenario_id} is not AgentOutput"

    def test_response_keys_match_filenames(self):
        response_files = {p.stem for p in (_DATA_DIR / "responses").glob("*.json")}
        assert set(_LOADED_RESPONSES.keys()) == response_files

    def test_transcripts_are_valid(self):
        for scenario_id, output in _LOADED_RESPONSES.items():
            assert isinstance(output.transcript, ConversationTranscript)
            assert output.transcript.scenario_id == scenario_id

    def test_intake_records_are_valid(self):
        for scenario_id, output in _LOADED_RESPONSES.items():
            assert isinstance(output.intake_record, StructuredIntakeRecord)
            assert output.intake_record.caregiver.caregiver_id

    def test_action_logs_are_valid(self):
        for scenario_id, output in _LOADED_RESPONSES.items():
            assert isinstance(output.action_log, AgentActionLog)
            assert output.action_log.scenario_id == scenario_id


class TestMockAgentJsonIntegration:
    """Test MockAgent uses JSON-loaded responses correctly."""

    def setup_method(self):
        self.agent = MockAgent()

    def test_run_all_loaded_scenarios(self):
        """Every loaded response can be retrieved via run_scenario."""
        for scenario_id in _LOADED_RESPONSES:
            output = self.agent.run_scenario(_make_scenario(scenario_id))
            assert output.transcript.scenario_id == scenario_id

    def test_custom_builder_overrides_json(self):
        """A registered builder takes precedence over JSON-loaded data."""
        def custom_builder(sid: str) -> AgentOutput:
            return AgentOutput(
                transcript=ConversationTranscript(scenario_id=sid, turns=[]),
                intake_record=StructuredIntakeRecord(
                    caregiver={"caregiver_id": "override", "full_name": "Override"},
                ),
                action_log=AgentActionLog(scenario_id=sid),
            )

        self.agent.register("compliance_cpr_missing", custom_builder)
        output = self.agent.run_scenario(_make_scenario("compliance_cpr_missing"))
        assert output.intake_record.caregiver.caregiver_id == "override"

    def test_unknown_scenario_error_lists_all_known(self):
        with pytest.raises(ValueError, match="compliance_cpr_missing"):
            self.agent.run_scenario(_make_scenario("nonexistent"))

    def test_json_response_round_trip(self):
        """Verify that loading a JSON response produces the same data as the original."""
        for path in sorted((_DATA_DIR / "responses").glob("*.json")):
            raw = json.loads(path.read_text())
            scenario_id = path.stem
            output = _LOADED_RESPONSES[scenario_id]

            # Re-serialize and compare
            reserialized = {
                "transcript": output.transcript.model_dump(mode="json"),
                "intake_record": output.intake_record.model_dump(mode="json"),
                "action_log": output.action_log.model_dump(mode="json"),
            }
            assert reserialized == raw, f"Round-trip mismatch for {scenario_id}"
