"""Quality gate enforcement for evaluation results."""

from __future__ import annotations

from dataclasses import dataclass, field

from eval_caregiver.schemas.grader_results import ScenarioResult


@dataclass
class QualityGate:
    """A single quality gate with a metric name and threshold."""

    metric: str
    threshold: float
    description: str = ""


@dataclass
class QualityGateResult:
    """Result of evaluating a single quality gate."""

    gate: QualityGate
    actual_value: float
    passed: bool


@dataclass
class QualityGateReport:
    """Overall quality gate evaluation report."""

    gate_results: list[QualityGateResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(gr.passed for gr in self.gate_results)


DEFAULT_GATES = [
    QualityGate(
        metric="compliance_gap_detection_recall",
        threshold=0.95,
        description="Agent must detect >= 95% of compliance gaps",
    ),
    QualityGate(
        metric="compliance_remediation_success",
        threshold=0.85,
        description="Agent must offer remediation >= 85% of the time",
    ),
    QualityGate(
        metric="safe_area_suggestion_quality",
        threshold=0.80,
        description="Safety area suggestion quality >= 80%",
    ),
]

# Maps quality gate metrics to grader names
_METRIC_TO_GRADER = {
    "compliance_gap_detection_recall": "compliance_gap_detection",
    "compliance_remediation_success": "compliance_remediation",
    "safe_area_suggestion_quality": "safe_area_suggestion_quality",
}


class QualityGateEvaluator:
    """Evaluates scenario results against quality gates."""

    def __init__(self, gates: list[QualityGate] | None = None) -> None:
        self._gates = gates if gates is not None else list(DEFAULT_GATES)

    def evaluate(self, results: list[ScenarioResult]) -> QualityGateReport:
        """Evaluate all quality gates against scenario results."""
        gate_results = []
        for gate in self._gates:
            grader_name = _METRIC_TO_GRADER.get(gate.metric, gate.metric)
            scores = self._collect_scores(results, grader_name)
            avg_score = sum(scores) / len(scores) if scores else 1.0
            gate_results.append(
                QualityGateResult(
                    gate=gate,
                    actual_value=avg_score,
                    passed=avg_score >= gate.threshold,
                )
            )
        return QualityGateReport(gate_results=gate_results)

    def _collect_scores(self, results: list[ScenarioResult], grader_name: str) -> list[float]:
        """Collect all scores for a specific grader across required scenarios."""
        scores = []
        for result in results:
            for gr in result.grader_results:
                if gr.grader_name == grader_name:
                    scores.append(gr.score)
        return scores
