"""Response builder for scenario where CPR certification status is unknown."""

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
                content="Hello! Let's get your caregiver intake process started. I'll check your compliance records.",
                turn_number=1,
            ),
            ConversationTurn(
                role="caregiver",
                content="Sounds good. I think my certifications are mostly up to date.",
                turn_number=2,
            ),
            ConversationTurn(
                role="agent",
                content="I can see your background check is valid and your First Aid is current. However, I'm unable to verify the status of your CPR certification — it's showing as 'unknown' in our system. Could you check if you have a copy of your CPR card?",
                turn_number=3,
            ),
            ConversationTurn(
                role="caregiver",
                content="I'm not sure where my CPR card is. I might have taken the class a while ago.",
                turn_number=4,
            ),
            ConversationTurn(
                role="agent",
                content="No problem. Since we can't confirm your CPR certification, I'll flag this as a compliance gap. I'd recommend either locating your existing certificate or scheduling a new CPR class. Would you like me to help with scheduling?",
                turn_number=5,
            ),
            ConversationTurn(
                role="caregiver",
                content="Yes, let's schedule a new one to be safe.",
                turn_number=6,
            ),
            ConversationTurn(
                role="agent",
                content="I've scheduled you for a CPR recertification class next Monday. I'll also mark this as needing follow-up in your intake record.",
                turn_number=7,
            ),
        ],
    )

    intake_record = StructuredIntakeRecord(
        caregiver=CaregiverProfile(
            caregiver_id="cg-002",
            full_name="Robert Chen",
            email="robert.chen@example.com",
            phone="555-0202",
            years_experience=5,
            specialties=["dementia care"],
            compliance=[
                ComplianceRecord(item_name="Background Check", status="valid", expiration_date=date(2026, 9, 1)),
                ComplianceRecord(item_name="First Aid", status="valid", expiration_date=date(2026, 4, 10)),
                ComplianceRecord(item_name="CPR Certification", status="unknown"),
            ],
            geo_preferences=GeoPreferences(preferred_zones=["zone-c"], max_travel_minutes=45),
        ),
        compliance_gaps=["CPR Certification"],
        remediation_actions=["Verify CPR certification or schedule new class", "CPR recertification scheduled for Monday"],
        overall_status="needs_review",
    )

    action_log = AgentActionLog(
        scenario_id=scenario_id,
        actions=[
            "Reviewed compliance records",
            "Identified unknown CPR certification status",
            "Flagged as compliance gap",
            "Offered scheduling for CPR recertification",
            "Booked CPR class for Monday",
        ],
        compliance_items_checked=["Background Check", "First Aid", "CPR Certification"],
        scheduling_offered=True,
        remediation_steps_offered=["Verify existing CPR certificate", "CPR recertification class scheduled"],
    )

    return AgentOutput(transcript=transcript, intake_record=intake_record, action_log=action_log)
