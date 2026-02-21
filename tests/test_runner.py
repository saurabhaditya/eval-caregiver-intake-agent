"""Tests for the evaluation executor."""

from eval_caregiver.agent.mock_agent import MockAgent
from eval_caregiver.graders.code_based.compliance_gap import ComplianceGapGrader
from eval_caregiver.graders.code_based.compliance_remediation import ComplianceRemediationGrader
from eval_caregiver.graders.code_based.geo_restriction import GeoRestrictionGrader
from eval_caregiver.runner.executor import EvalExecutor
from eval_caregiver.scenarios.loader import get_all_scenarios, get_collection


def _build_graders():
    graders = [ComplianceGapGrader(), ComplianceRemediationGrader(), GeoRestrictionGrader()]
    return {g.name: g for g in graders}


class TestEvalExecutor:
    def test_run_single_scenario(self):
        agent = MockAgent()
        graders = _build_graders()
        executor = EvalExecutor(agent=agent, graders=graders, skip_model_graders=True)

        scenario = get_collection("compliance_missing_cases").scenarios[0]
        result = executor.run_scenario(scenario)
        assert result.scenario_id == "compliance_cpr_missing"
        assert result.passed is True
        assert len(result.grader_results) > 0

    def test_run_all_scenarios(self):
        agent = MockAgent()
        graders = _build_graders()
        executor = EvalExecutor(agent=agent, graders=graders, skip_model_graders=True)

        scenarios = get_all_scenarios()
        results = executor.run_scenarios(scenarios)
        assert len(results) == len(scenarios)

    def test_skip_model_graders(self):
        """Verify model-based graders are skipped when flag is set."""
        from eval_caregiver.graders.model_based.safety_map_suggestions import SafetyMapSuggestionsGrader

        agent = MockAgent()
        graders = _build_graders()
        model_grader = SafetyMapSuggestionsGrader()
        graders[model_grader.name] = model_grader

        executor = EvalExecutor(agent=agent, graders=graders, skip_model_graders=True)
        scenario = get_collection("geo_over_restriction_cases").scenarios[0]
        result = executor.run_scenario(scenario)

        grader_names_used = [gr.grader_name for gr in result.grader_results]
        assert "safe_area_suggestion_quality" not in grader_names_used

    def test_compliance_scenarios_pass(self):
        agent = MockAgent()
        graders = _build_graders()
        executor = EvalExecutor(agent=agent, graders=graders, skip_model_graders=True)

        collection = get_collection("compliance_missing_cases")
        results = executor.run_scenarios(collection.scenarios)
        required_results = [r for r, s in zip(results, collection.scenarios) if s.required]
        assert all(r.passed for r in required_results)

    def test_geo_scenario_expected_failure(self):
        """The geo_no_alternatives scenario should fail the geo grader."""
        agent = MockAgent()
        graders = _build_graders()
        executor = EvalExecutor(agent=agent, graders=graders, skip_model_graders=True)

        collection = get_collection("geo_over_restriction_cases")
        # geo_no_alternatives is the second scenario
        negative_scenario = collection.scenarios[1]
        result = executor.run_scenario(negative_scenario)
        assert result.passed is False

    def test_manual_review_flagged_on_failure(self):
        agent = MockAgent()
        graders = _build_graders()
        executor = EvalExecutor(agent=agent, graders=graders, skip_model_graders=True)

        collection = get_collection("geo_over_restriction_cases")
        negative_scenario = collection.scenarios[1]
        result = executor.run_scenario(negative_scenario)
        assert result.needs_manual_review is True
        assert len(result.review_reasons) > 0
