"""Response builder for scenario where CPR certification is missing."""

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
                content="Welcome! I'm here to help with your caregiver intake. Let me start by reviewing your compliance records.",
                turn_number=1,
            ),
            ConversationTurn(
                role="caregiver",
                content="Sure, I have my background check and first aid cert ready.",
                turn_number=2,
            ),
            ConversationTurn(
                role="agent",
                content="Thank you. I can see your background check is valid and your First Aid certification is current. However, I notice that your CPR certification is missing from our records. CPR certification is required for all caregivers.",
                turn_number=3,
            ),
            ConversationTurn(
                role="caregiver",
                content="Oh, I didn't realize I needed that. What should I do?",
                turn_number=4,
            ),
            ConversationTurn(
                role="agent",
                content="No worries! I can help you schedule a CPR certification class. We have sessions available this week and next week. Would you like me to book one for you? In the meantime, I'll note this as a compliance gap that needs to be resolved before you can start assignments.",
                turn_number=5,
            ),
            ConversationTurn(
                role="caregiver",
                content="Yes, please schedule me for the earliest available class.",
                turn_number=6,
            ),
            ConversationTurn(
                role="agent",
                content="I've scheduled you for the CPR certification class on Thursday. You'll receive a confirmation email shortly. Once you complete the class, your compliance record will be updated automatically.",
                turn_number=7,
            ),
        ],
    )

    intake_record = StructuredIntakeRecord(
        caregiver=CaregiverProfile(
            caregiver_id="cg-001",
            full_name="Jane Smith",
            email="jane.smith@example.com",
            phone="555-0101",
            years_experience=3,
            specialties=["elderly care", "mobility assistance"],
            compliance=[
                ComplianceRecord(item_name="Background Check", status="valid", expiration_date=date(2026, 6, 15)),
                ComplianceRecord(item_name="First Aid", status="valid", expiration_date=date(2026, 3, 20)),
                ComplianceRecord(item_name="CPR Certification", status="missing"),
            ],
            geo_preferences=GeoPreferences(preferred_zones=["zone-a", "zone-b"], max_travel_minutes=30),
        ),
        compliance_gaps=["CPR Certification"],
        remediation_actions=["Schedule CPR certification class", "CPR class booked for Thursday"],
        overall_status="needs_review",
    )

    action_log = AgentActionLog(
        scenario_id=scenario_id,
        actions=[
            "Reviewed compliance records",
            "Identified missing CPR certification",
            "Offered scheduling for CPR class",
            "Booked CPR class for Thursday",
        ],
        compliance_items_checked=["Background Check", "First Aid", "CPR Certification"],
        scheduling_offered=True,
        remediation_steps_offered=["Schedule CPR certification class", "CPR class booked for Thursday"],
    )

    return AgentOutput(transcript=transcript, intake_record=intake_record, action_log=action_log)
