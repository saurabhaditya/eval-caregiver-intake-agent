"""Response builder for scenario where CPR certification is present and valid (optional, should pass)."""

from __future__ import annotations

from datetime import date

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
                content="Welcome! Let me review your compliance records to get your intake started.",
                turn_number=1,
            ),
            ConversationTurn(
                role="caregiver",
                content="Great, I have all my certifications ready.",
                turn_number=2,
            ),
            ConversationTurn(
                role="agent",
                content="Excellent! I can see that your Background Check, First Aid certification, and CPR certification are all valid and up to date. You're fully compliant — no action needed on the certification front.",
                turn_number=3,
            ),
            ConversationTurn(
                role="caregiver",
                content="That's good to hear!",
                turn_number=4,
            ),
            ConversationTurn(
                role="agent",
                content="Let's move on to discussing your geographic preferences and availability.",
                turn_number=5,
            ),
        ],
    )

    intake_record = StructuredIntakeRecord(
        caregiver=CaregiverProfile(
            caregiver_id="cg-003",
            full_name="Maria Garcia",
            email="maria.garcia@example.com",
            phone="555-0303",
            years_experience=8,
            specialties=["pediatric care", "elderly care"],
            compliance=[
                ComplianceRecord(item_name="Background Check", status="valid", expiration_date=date(2027, 1, 15)),
                ComplianceRecord(item_name="First Aid", status="valid", expiration_date=date(2026, 8, 20)),
                ComplianceRecord(item_name="CPR Certification", status="valid", expiration_date=date(2026, 11, 5)),
            ],
            geo_preferences=GeoPreferences(
                preferred_zones=["zone-a", "zone-b", "zone-c"],
                max_travel_minutes=60,
                has_own_transport=True,
            ),
        ),
        compliance_gaps=[],
        remediation_actions=[],
        overall_status="complete",
    )

    action_log = AgentActionLog(
        scenario_id=scenario_id,
        actions=[
            "Reviewed compliance records",
            "Confirmed all certifications are valid",
        ],
        compliance_items_checked=["Background Check", "First Aid", "CPR Certification"],
        scheduling_offered=False,
        remediation_steps_offered=[],
    )

    return AgentOutput(transcript=transcript, intake_record=intake_record, action_log=action_log)
