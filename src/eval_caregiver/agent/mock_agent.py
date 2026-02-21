"""Mock agent that dispatches to canned response builders by scenario_id."""

from __future__ import annotations

from typing import Callable

from eval_caregiver.agent.base import AgentBase, AgentOutput
from eval_caregiver.agent.responses import (
    cpr_missing,
    cpr_present,
    cpr_unknown,
    geo_no_alternatives,
    geo_restricted,
)
from eval_caregiver.schemas.scenarios import TestScenario

# Registry: scenario_id → response builder function
_RESPONSE_REGISTRY: dict[str, Callable[[str], AgentOutput]] = {
    "compliance_cpr_missing": cpr_missing.build,
    "compliance_cpr_unknown": cpr_unknown.build,
    "compliance_cpr_present": cpr_present.build,
    "geo_over_restricted": geo_restricted.build,
    "geo_no_alternatives": geo_no_alternatives.build,
}


class MockAgent(AgentBase):
    """A mock agent that returns pre-built responses for known scenario IDs."""

    def __init__(self) -> None:
        self._registry = dict(_RESPONSE_REGISTRY)

    def register(self, scenario_id: str, builder: Callable[[str], AgentOutput]) -> None:
        """Register a custom response builder for a scenario."""
        self._registry[scenario_id] = builder

    def run_scenario(self, scenario: TestScenario) -> AgentOutput:
        builder = self._registry.get(scenario.scenario_id)
        if builder is None:
            raise ValueError(
                f"No response registered for scenario_id={scenario.scenario_id!r}. "
                f"Known scenarios: {sorted(self._registry.keys())}"
            )
        return builder(scenario.scenario_id)
