"""Tests for code-based (deterministic) graders."""

from datetime import date

import pytest

from eval_caregiver.graders.code_based.compliance_gap import ComplianceGapGrader
from eval_caregiver.graders.code_based.compliance_remediation import ComplianceRemediationGrader
from eval_caregiver.graders.code_based.geo_restriction import GeoRestrictionGrader
from eval_caregiver.schemas.caregiver import (
    CaregiverProfile,
    ComplianceRecord,
    GeoPreferences,
    StructuredIntakeRecord,
)
from eval_caregiver.schemas.conversation import AgentActionLog
from eval_caregiver.schemas.scenarios import TestScenario


class TestComplianceGapGrader:
    def setup_method(self):
        self.grader = ComplianceGapGrader()

    def test_name(self):
        assert self.grader.name == "compliance_gap_detection"

    def test_is_not_model_based(self):
        assert self.grader.is_model_based is False

    def test_all_gaps_detected(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["compliance_gap_detection"],
            expected_compliance_gaps=["CPR Certification"],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            compliance_gaps=["CPR Certification"],
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake)
        assert result.passed is True
        assert result.score == 1.0

    def test_gap_missed(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["compliance_gap_detection"],
            expected_compliance_gaps=["CPR Certification"],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            compliance_gaps=[],
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake)
        assert result.passed is False
        assert result.score == 0.0

    def test_no_expected_gaps(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["compliance_gap_detection"],
            expected_compliance_gaps=[],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            compliance_gaps=[],
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake)
        assert result.passed is True
        assert result.score == 1.0


class TestComplianceRemediationGrader:
    def setup_method(self):
        self.grader = ComplianceRemediationGrader()

    def test_name(self):
        assert self.grader.name == "compliance_remediation"

    def test_full_remediation(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["compliance_remediation"],
            expected_compliance_gaps=["CPR Certification"],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            compliance_gaps=["CPR Certification"],
            remediation_actions=["Schedule CPR class"],
        )
        action_log = AgentActionLog(
            scenario_id="test",
            scheduling_offered=True,
            remediation_steps_offered=["Schedule CPR class"],
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake, action_log=action_log)
        assert result.passed is True
        assert result.score == 1.0

    def test_no_remediation(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["compliance_remediation"],
            expected_compliance_gaps=["CPR Certification"],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            compliance_gaps=["CPR Certification"],
            remediation_actions=[],
        )
        action_log = AgentActionLog(
            scenario_id="test",
            scheduling_offered=False,
            remediation_steps_offered=[],
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake, action_log=action_log)
        assert result.passed is False
        assert result.score == 0.0

    def test_no_gaps_expected(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["compliance_remediation"],
            expected_compliance_gaps=[],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
        )
        action_log = AgentActionLog(scenario_id="test")
        result = self.grader.grade(scenario=scenario, intake_record=intake, action_log=action_log)
        assert result.passed is True


class TestGeoRestrictionGrader:
    def setup_method(self):
        self.grader = GeoRestrictionGrader()

    def test_name(self):
        assert self.grader.name == "geo_restriction_detection"

    def test_full_detection_with_suggestions(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["geo_restriction_detection"],
            expected_geo_concerns=["over_restricted_zones", "limited_assignment_availability"],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            geo_concerns=["over_restricted_zones", "limited_assignment_availability"],
            safe_area_suggestions=["Zone B (low risk)"],
        )
        action_log = AgentActionLog(
            scenario_id="test",
            safety_map_consulted=True,
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake, action_log=action_log)
        assert result.passed is True
        assert result.score == 1.0

    def test_no_detection(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["geo_restriction_detection"],
            expected_geo_concerns=["over_restricted_zones"],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
            geo_concerns=[],
            safe_area_suggestions=[],
        )
        action_log = AgentActionLog(
            scenario_id="test",
            safety_map_consulted=False,
        )
        result = self.grader.grade(scenario=scenario, intake_record=intake, action_log=action_log)
        assert result.passed is False
        assert result.score == 0.0

    def test_no_expected_concerns(self):
        scenario = TestScenario(
            scenario_id="test",
            name="Test",
            description="Test",
            collection="test",
            grader_names=["geo_restriction_detection"],
            expected_geo_concerns=[],
        )
        intake = StructuredIntakeRecord(
            caregiver=CaregiverProfile(caregiver_id="cg-1", full_name="Test"),
        )
        action_log = AgentActionLog(scenario_id="test")
        result = self.grader.grade(scenario=scenario, intake_record=intake, action_log=action_log)
        assert result.passed is True
