from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from eval_caregiver.schemas.caregiver import StructuredIntakeRecord
from eval_caregiver.schemas.conversation import AgentActionLog, ConversationTranscript
from eval_caregiver.schemas.scenarios import TestScenario


@dataclass
class AgentOutput:
    """Output from running an agent on a scenario."""

    transcript: ConversationTranscript
    intake_record: StructuredIntakeRecord
    action_log: AgentActionLog


class AgentBase(ABC):
    """Abstract base class for agents (real or mock)."""

    @abstractmethod
    def run_scenario(self, scenario: TestScenario) -> AgentOutput:
        """Run the agent on a given test scenario and return its output."""
        ...
