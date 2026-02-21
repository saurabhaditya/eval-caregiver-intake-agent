"""Mock agent that loads canned responses from JSON data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from eval_caregiver.agent.base import AgentBase, AgentOutput
from eval_caregiver.schemas.caregiver import StructuredIntakeRecord
from eval_caregiver.schemas.conversation import AgentActionLog, ConversationTranscript
from eval_caregiver.schemas.scenarios import TestScenario

_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _load_responses() -> dict[str, AgentOutput]:
    """Scan data/responses/*.json and build AgentOutput for each."""
    responses: dict[str, AgentOutput] = {}
    responses_dir = _DATA_DIR / "responses"
    for path in sorted(responses_dir.glob("*.json")):
        raw = json.loads(path.read_text())
        output = AgentOutput(
            transcript=ConversationTranscript.model_validate(raw["transcript"]),
            intake_record=StructuredIntakeRecord.model_validate(raw["intake_record"]),
            action_log=AgentActionLog.model_validate(raw["action_log"]),
        )
        scenario_id = path.stem
        responses[scenario_id] = output
    return responses


_LOADED_RESPONSES: dict[str, AgentOutput] = _load_responses()


class MockAgent(AgentBase):
    """A mock agent that returns pre-built responses for known scenario IDs."""

    def __init__(self) -> None:
        self._responses: dict[str, AgentOutput] = dict(_LOADED_RESPONSES)
        self._builders: dict[str, Callable[[str], AgentOutput]] = {}

    def register(self, scenario_id: str, builder: Callable[[str], AgentOutput]) -> None:
        """Register a custom response builder for a scenario."""
        self._builders[scenario_id] = builder

    def run_scenario(self, scenario: TestScenario) -> AgentOutput:
        builder = self._builders.get(scenario.scenario_id)
        if builder is not None:
            return builder(scenario.scenario_id)

        output = self._responses.get(scenario.scenario_id)
        if output is not None:
            return output

        known = sorted(set(list(self._responses.keys()) + list(self._builders.keys())))
        raise ValueError(
            f"No response registered for scenario_id={scenario.scenario_id!r}. "
            f"Known scenarios: {known}"
        )
