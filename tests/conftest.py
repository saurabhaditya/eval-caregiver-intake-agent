"""Shared fixtures for the test suite."""

from __future__ import annotations

from datetime import date

import pytest

from eval_caregiver.agent.base import AgentOutput
from eval_caregiver.agent.mock_agent import MockAgent
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
from eval_caregiver.schemas.scenarios import TestScenario


@pytest.fixture
def mock_agent() -> MockAgent:
    return MockAgent()


@pytest.fixture
def compliance_scenario() -> TestScenario:
    return TestScenario(
        scenario_id="compliance_cpr_missing",
        name="CPR Certification Missing",
        description="Caregiver is missing CPR certification.",
        collection="compliance_missing_cases",
        required=True,
        grader_names=["compliance_gap_detection", "compliance_remediation"],
        expected_compliance_gaps=["CPR Certification"],
    )


@pytest.fixture
def geo_scenario() -> TestScenario:
    return TestScenario(
        scenario_id="geo_over_restricted",
        name="Over-Restricted Zones",
        description="Caregiver has over-restricted geographic preferences.",
        collection="geo_over_restriction_cases",
        required=True,
        grader_names=["geo_restriction_detection"],
        expected_geo_concerns=["over_restricted_zones", "limited_assignment_availability"],
    )


@pytest.fixture
def sample_intake_record() -> StructuredIntakeRecord:
    return StructuredIntakeRecord(
        caregiver=CaregiverProfile(
            caregiver_id="cg-test",
            full_name="Test User",
            compliance=[
                ComplianceRecord(item_name="Background Check", status="valid", expiration_date=date(2026, 6, 15)),
                ComplianceRecord(item_name="CPR Certification", status="missing"),
            ],
            geo_preferences=GeoPreferences(preferred_zones=["zone-a"]),
        ),
        compliance_gaps=["CPR Certification"],
        remediation_actions=["Schedule CPR class"],
        overall_status="needs_review",
    )


@pytest.fixture
def sample_transcript() -> ConversationTranscript:
    return ConversationTranscript(
        scenario_id="test",
        turns=[
            ConversationTurn(role="agent", content="Hello, let me check your records.", turn_number=1),
            ConversationTurn(role="caregiver", content="Sure.", turn_number=2),
            ConversationTurn(role="agent", content="Your CPR cert is missing.", turn_number=3),
        ],
    )


@pytest.fixture
def sample_action_log() -> AgentActionLog:
    return AgentActionLog(
        scenario_id="test",
        actions=["Checked compliance", "Identified gap"],
        compliance_items_checked=["Background Check", "CPR Certification"],
        scheduling_offered=True,
        remediation_steps_offered=["Schedule CPR class"],
    )
