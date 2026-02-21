"""Response builder for scenario where caregiver has over-restricted their geographic preferences."""

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
                content="Let's review your geographic preferences. I see you've selected only Zone A and excluded several zones.",
                turn_number=1,
            ),
            ConversationTurn(
                role="caregiver",
                content="Yes, I only want to work in Zone A. I've heard the other areas aren't safe.",
                turn_number=2,
            ),
            ConversationTurn(
                role="agent",
                content="I understand your concern about safety. Let me check our safety map for the latest information. According to our current safety map, Zone B and Zone C are both classified as 'low risk' areas. Zone D is 'medium risk' but has high patient demand. Only Zone E is currently flagged as 'high risk'.",
                turn_number=3,
            ),
            ConversationTurn(
                role="caregiver",
                content="Oh, I didn't know that. I was just being cautious.",
                turn_number=4,
            ),
            ConversationTurn(
                role="agent",
                content="That's completely understandable! Based on the safety data, you might want to consider adding Zone B and Zone C to your preferred areas — they're both low risk and have good patient demand. This would significantly increase your available assignments. Zone D also has many patients who need help, though I understand if you'd prefer to stick with low-risk areas for now.",
                turn_number=5,
            ),
            ConversationTurn(
                role="caregiver",
                content="I'll think about adding Zone B. Thanks for the information.",
                turn_number=6,
            ),
            ConversationTurn(
                role="agent",
                content="You're welcome! I'll note that you're currently limited to Zone A but may expand to Zone B. I'd recommend revisiting this after your first few assignments. Would you like me to set a reminder to review your geographic preferences in two weeks?",
                turn_number=7,
            ),
        ],
    )

    intake_record = StructuredIntakeRecord(
        caregiver=CaregiverProfile(
            caregiver_id="cg-004",
            full_name="David Park",
            email="david.park@example.com",
            phone="555-0404",
            years_experience=2,
            specialties=["elderly care"],
            compliance=[
                ComplianceRecord(item_name="Background Check", status="valid"),
                ComplianceRecord(item_name="CPR Certification", status="valid"),
            ],
            geo_preferences=GeoPreferences(
                preferred_zones=["zone-a"],
                excluded_zones=["zone-b", "zone-c", "zone-d", "zone-e"],
                max_travel_minutes=20,
                has_own_transport=False,
            ),
        ),
        compliance_gaps=[],
        geo_concerns=["over_restricted_zones", "limited_assignment_availability"],
        safe_area_suggestions=["Zone B (low risk)", "Zone C (low risk)", "Zone D (medium risk, high demand)"],
        overall_status="needs_review",
    )

    action_log = AgentActionLog(
        scenario_id=scenario_id,
        actions=[
            "Reviewed geographic preferences",
            "Consulted safety map",
            "Identified over-restriction",
            "Suggested safe alternative zones",
            "Offered to set reminder for preference review",
        ],
        compliance_items_checked=[],
        safety_map_consulted=True,
        scheduling_offered=False,
        remediation_steps_offered=["Review geographic preferences in two weeks"],
    )

    return AgentOutput(transcript=transcript, intake_record=intake_record, action_log=action_log)
