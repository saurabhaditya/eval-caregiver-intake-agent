from __future__ import annotations

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """A single turn in a conversation transcript."""

    role: str = Field(description="Role: 'agent' or 'caregiver'")
    content: str = Field(description="The message content")
    turn_number: int = Field(description="Sequential turn number (1-indexed)")


class ConversationTranscript(BaseModel):
    """Full conversation transcript between agent and caregiver."""

    scenario_id: str = Field(description="The scenario this conversation belongs to")
    turns: list[ConversationTurn] = Field(default_factory=list, description="Ordered conversation turns")

    @property
    def full_text(self) -> str:
        """Return the full conversation as a single string."""
        lines = []
        for turn in self.turns:
            role_label = "Agent" if turn.role == "agent" else "Caregiver"
            lines.append(f"{role_label}: {turn.content}")
        return "\n\n".join(lines)


class AgentActionLog(BaseModel):
    """Log of actions the agent took during a scenario."""

    scenario_id: str = Field(description="The scenario this log belongs to")
    actions: list[str] = Field(default_factory=list, description="List of actions taken by the agent")
    compliance_items_checked: list[str] = Field(
        default_factory=list, description="Compliance items the agent checked"
    )
    safety_map_consulted: bool = Field(default=False, description="Whether the agent consulted the safety map")
    scheduling_offered: bool = Field(default=False, description="Whether the agent offered scheduling")
    remediation_steps_offered: list[str] = Field(
        default_factory=list, description="Remediation steps the agent offered"
    )
