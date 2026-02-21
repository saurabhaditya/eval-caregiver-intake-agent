"""Tests for quality gate evaluation."""

from eval_caregiver.runner.quality_gates import (
    DEFAULT_GATES,
    QualityGate,
    QualityGateEvaluator,
)
from eval_caregiver.schemas.grader_results import GraderResult, ScenarioResult


def _make_result(scenario_id: str, grader_name: str, score: float, passed: bool) -> ScenarioResult:
    return ScenarioResult(
        scenario_id=scenario_id,
        scenario_name=f"Test {scenario_id}",
        grader_results=[
            GraderResult(grader_name=grader_name, passed=passed, score=score)
        ],
        passed=passed,
    )


class TestQualityGateEvaluator:
    def test_all_gates_pass(self):
        results = [
            _make_result("s1", "compliance_gap_detection", 1.0, True),
            _make_result("s2", "compliance_remediation", 1.0, True),
            _make_result("s3", "safe_area_suggestion_quality", 1.0, True),
        ]
        evaluator = QualityGateEvaluator()
        report = evaluator.evaluate(results)
        assert report.all_passed is True

    def test_compliance_gap_gate_fails(self):
        results = [
            _make_result("s1", "compliance_gap_detection", 0.5, False),
            _make_result("s2", "compliance_remediation", 1.0, True),
            _make_result("s3", "safe_area_suggestion_quality", 1.0, True),
        ]
        evaluator = QualityGateEvaluator()
        report = evaluator.evaluate(results)
        assert report.all_passed is False

        # Find the specific gate that failed
        gap_gate = next(gr for gr in report.gate_results if gr.gate.metric == "compliance_gap_detection_recall")
        assert gap_gate.passed is False
        assert gap_gate.actual_value == 0.5

    def test_custom_gates(self):
        gates = [QualityGate(metric="compliance_gap_detection", threshold=0.50)]
        results = [_make_result("s1", "compliance_gap_detection", 0.6, True)]
        evaluator = QualityGateEvaluator(gates=gates)
        report = evaluator.evaluate(results)
        assert report.all_passed is True

    def test_no_relevant_scores(self):
        """When no scores match a gate metric, it should pass (no data = no failure)."""
        results = [_make_result("s1", "unrelated_grader", 0.0, False)]
        evaluator = QualityGateEvaluator()
        report = evaluator.evaluate(results)
        assert report.all_passed is True

    def test_default_gates_exist(self):
        assert len(DEFAULT_GATES) == 3
        metrics = [g.metric for g in DEFAULT_GATES]
        assert "compliance_gap_detection_recall" in metrics
        assert "compliance_remediation_success" in metrics
        assert "safe_area_suggestion_quality" in metrics

    def test_multiple_scores_averaged(self):
        """Multiple scores for the same grader should be averaged."""
        results = [
            _make_result("s1", "compliance_gap_detection", 1.0, True),
            _make_result("s2", "compliance_gap_detection", 0.5, False),
        ]
        evaluator = QualityGateEvaluator()
        report = evaluator.evaluate(results)
        gap_gate = next(gr for gr in report.gate_results if gr.gate.metric == "compliance_gap_detection_recall")
        assert gap_gate.actual_value == 0.75
        assert gap_gate.passed is False  # 0.75 < 0.95
