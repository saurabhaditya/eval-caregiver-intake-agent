"""Response builder for scenario where agent fails to suggest alternatives for over-restricted geo.
This is an optional/negative test — the agent does NOT provide good suggestions."""

from __future__ import annotations

from eval_caregiver.agent.base import AgentOutput
from eval_caregiver.schemas.caregiver import (
    CaregiverProfile,
    ComplianceRecord,
    GeoPreferences,
    StructuredIntakeRecord,
)
from eval_caregiver.schemas.conversation import (
    AgentActionLog,
    ConversationTranscript,
    ConversationTurn,
)


def build(scenario_id: str) -> AgentOutput:
    transcript = ConversationTranscript(
        scenario_id=scenario_id,
        turns=[
            ConversationTurn(
                role="agent",
                content="I see your geographic preferences. You've selected only Zone A.",
                turn_number=1,
            ),
            ConversationTurn(
                role="caregiver",
                content="Yes, that's all I want to work in.",
                turn_number=2,
            ),
            ConversationTurn(
                role="agent",
                content="Understood. I'll note that you prefer Zone A. Let's continue with the rest of the intake.",
                turn_number=3,
            ),
        ],
    )

    intake_record = StructuredIntakeRecord(
        caregiver=CaregiverProfile(
            caregiver_id="cg-005",
            full_name="Lisa Wong",
            email="lisa.wong@example.com",
            phone="555-0505",
            years_experience=1,
            specialties=[],
            compliance=[
                ComplianceRecord(item_name="Background Check", status="valid"),
                ComplianceRecord(item_name="CPR Certification", status="valid"),
            ],
            geo_preferences=GeoPreferences(
                preferred_zones=["zone-a"],
                excluded_zones=["zone-b", "zone-c", "zone-d", "zone-e"],
                max_travel_minutes=15,
                has_own_transport=False,
            ),
        ),
        compliance_gaps=[],
        geo_concerns=[],
        safe_area_suggestions=[],
        overall_status="complete",
    )

    action_log = AgentActionLog(
        scenario_id=scenario_id,
        actions=["Reviewed geographic preferences", "Accepted preferences as-is"],
        compliance_items_checked=[],
        safety_map_consulted=False,
        scheduling_offered=False,
        remediation_steps_offered=[],
    )

    return AgentOutput(transcript=transcript, intake_record=intake_record, action_log=action_log)
