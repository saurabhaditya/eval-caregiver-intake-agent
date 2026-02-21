from __future__ import annotations

from abc import ABC, abstractmethod

from eval_caregiver.schemas.grader_results import GraderResult


class Grader(ABC):
    """Abstract base class for all graders."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this grader, used in scenario definitions."""
        ...

    @property
    def is_model_based(self) -> bool:
        """Whether this grader requires an LLM API call."""
        return False

    @abstractmethod
    def grade(self, **kwargs) -> GraderResult:
        """Evaluate agent output and return a grader result.

        Subclasses extract what they need from kwargs. Common keys:
        - transcript: ConversationTranscript
        - intake_record: StructuredIntakeRecord
        - action_log: AgentActionLog
        - scenario: TestScenario
        """
        ...
