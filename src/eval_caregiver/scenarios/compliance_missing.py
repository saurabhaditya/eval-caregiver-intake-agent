"""Compliance-related test scenarios: missing, unknown, and present CPR certification."""

from eval_caregiver.schemas.scenarios import ScenarioCollection, TestScenario

compliance_missing_cases = ScenarioCollection(
    collection_id="compliance_missing_cases",
    name="Compliance Missing Cases",
    description="Tests that the agent correctly identifies missing or unknown compliance items and offers remediation.",
    scenarios=[
        TestScenario(
            scenario_id="compliance_cpr_missing",
            name="CPR Certification Missing",
            description="Caregiver is missing CPR certification. Agent should detect the gap and offer scheduling.",
            collection="compliance_missing_cases",
            required=True,
            grader_names=["compliance_gap_detection", "compliance_remediation"],
            caregiver_setup={"cpr_status": "missing"},
            expected_compliance_gaps=["CPR Certification"],
        ),
        TestScenario(
            scenario_id="compliance_cpr_unknown",
            name="CPR Certification Unknown",
            description="Caregiver CPR status is unknown. Agent should flag it and help resolve.",
            collection="compliance_missing_cases",
            required=True,
            grader_names=["compliance_gap_detection", "compliance_remediation"],
            caregiver_setup={"cpr_status": "unknown"},
            expected_compliance_gaps=["CPR Certification"],
        ),
        TestScenario(
            scenario_id="compliance_cpr_present",
            name="CPR Certification Present (control)",
            description="All certifications are valid. Agent should confirm compliance with no gaps.",
            collection="compliance_missing_cases",
            required=False,
            grader_names=["compliance_gap_detection"],
            caregiver_setup={"cpr_status": "valid"},
            expected_compliance_gaps=[],
        ),
    ],
)
