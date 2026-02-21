"""Tests for Pydantic schema models."""

from datetime import date

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
from eval_caregiver.schemas.geo import PatientDemandSummary, SafetyMapReference, SafetyZone
from eval_caregiver.schemas.grader_results import GraderResult, RubricCriterionScore, ScenarioResult
from eval_caregiver.schemas.scenarios import ScenarioCollection, TestScenario


class TestComplianceRecord:
    def test_minimal(self):
        rec = ComplianceRecord(item_name="CPR", status="valid")
        assert rec.item_name == "CPR"
        assert rec.expiration_date is None

    def test_with_expiration(self):
        rec = ComplianceRecord(item_name="CPR", status="valid", expiration_date=date(2026, 12, 31))
        assert rec.expiration_date == date(2026, 12, 31)


class TestCaregiverProfile:
    def test_defaults(self):
        profile = CaregiverProfile(caregiver_id="cg-1", full_name="Test")
        assert profile.specialties == []
        assert profile.compliance == []
        assert isinstance(profile.geo_preferences, GeoPreferences)

    def test_full_profile(self):
        profile = CaregiverProfile(
            caregiver_id="cg-1",
            full_name="Jane Doe",
            email="jane@test.com",
            years_experience=5,
            specialties=["elderly care"],
            compliance=[ComplianceRecord(item_name="CPR", status="valid")],
            geo_preferences=GeoPreferences(preferred_zones=["zone-a"]),
        )
        assert len(profile.compliance) == 1
        assert profile.geo_preferences.preferred_zones == ["zone-a"]


class TestStructuredIntakeRecord:
    def test_defaults(self):
        record = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test")
        )
        assert record.compliance_gaps == []
        assert record.overall_status == "incomplete"


class TestConversationTranscript:
    def test_full_text(self):
        transcript = ConversationTranscript(
            scenario_id="test",
            turns=[
                ConversationTurn(role="agent", content="Hello", turn_number=1),
                ConversationTurn(role="caregiver", content="Hi", turn_number=2),
            ],
        )
        text = transcript.full_text
        assert "Agent: Hello" in text
        assert "Caregiver: Hi" in text


class TestGeoSchemas:
    def test_safety_zone(self):
        zone = SafetyZone(zone_id="z1", zone_name="Downtown", risk_level="low")
        assert zone.risk_level == "low"

    def test_safety_map(self):
        smap = SafetyMapReference(
            map_id="map-1",
            region="Metro",
            zones=[SafetyZone(zone_id="z1", zone_name="Downtown", risk_level="low")],
        )
        assert len(smap.zones) == 1

    def test_demand_summary(self):
        demand = PatientDemandSummary(
            zone_id="z1", zone_name="Downtown", demand_level="high", estimated_weekly_hours=40.0
        )
        assert demand.demand_level == "high"


class TestGraderResults:
    def test_grader_result(self):
        result = GraderResult(grader_name="test", passed=True, score=0.95, details="All good")
        assert result.passed
        assert result.score == 0.95

    def test_rubric_score(self):
        score = RubricCriterionScore(criterion="clarity", score=2, max_score=2, rationale="Clear")
        assert score.score == 2

    def test_scenario_result_overall_score(self):
        result = ScenarioResult(
            scenario_id="test",
            scenario_name="Test",
            grader_results=[
                GraderResult(grader_name="g1", passed=True, score=1.0),
                GraderResult(grader_name="g2", passed=True, score=0.5),
            ],
            passed=True,
        )
        assert result.overall_score == 0.75

    def test_scenario_result_empty(self):
        result = ScenarioResult(scenario_id="test", scenario_name="Test")
        assert result.overall_score == 0.0


class TestScenarios:
    def test_test_scenario(self):
        scenario = TestScenario(
            scenario_id="s1",
            name="Test Scenario",
            description="A test",
            collection="test_collection",
            grader_names=["g1", "g2"],
            expected_compliance_gaps=["CPR"],
        )
        assert scenario.required is True
        assert len(scenario.grader_names) == 2

    def test_scenario_collection(self):
        coll = ScenarioCollection(
            collection_id="c1",
            name="Test Collection",
            description="Tests",
            scenarios=[
                TestScenario(
                    scenario_id="s1",
                    name="S1",
                    description="Test",
                    collection="c1",
                    grader_names=["g1"],
                ),
            ],
        )
        assert len(coll.scenarios) == 1
