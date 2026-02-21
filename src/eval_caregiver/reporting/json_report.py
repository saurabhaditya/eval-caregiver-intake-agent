"""Machine-readable JSON report generation."""

from __future__ import annotations

import json
from pathlib import Path

from eval_caregiver.runner.quality_gates import QualityGateReport
from eval_caregiver.schemas.grader_results import ScenarioResult


def generate_json_report(
    results: list[ScenarioResult],
    gate_report: QualityGateReport,
    output_path: str = "output/eval_report.json",
) -> Path:
    """Generate a JSON evaluation report."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "summary": {
            "total_scenarios": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "needs_review": sum(1 for r in results if r.needs_manual_review),
            "quality_gates_passed": gate_report.all_passed,
        },
        "quality_gates": [
            {
                "metric": gr.gate.metric,
                "threshold": gr.gate.threshold,
                "actual": round(gr.actual_value, 4),
                "passed": gr.passed,
                "description": gr.gate.description,
            }
            for gr in gate_report.gate_results
        ],
        "scenarios": [
            {
                "scenario_id": r.scenario_id,
                "scenario_name": r.scenario_name,
                "passed": r.passed,
                "overall_score": round(r.overall_score, 4),
                "needs_manual_review": r.needs_manual_review,
                "review_reasons": r.review_reasons,
                "graders": [
                    {
                        "grader_name": gr.grader_name,
                        "passed": gr.passed,
                        "score": round(gr.score, 4),
                        "details": gr.details,
                        "criterion_scores": [
                            {
                                "criterion": cs.criterion,
                                "score": cs.score,
                                "max_score": cs.max_score,
                                "rationale": cs.rationale,
                            }
                            for cs in gr.criterion_scores
                        ],
                    }
                    for gr in r.grader_results
                ],
            }
            for r in results
        ],
    }

    path.write_text(json.dumps(report, indent=2))
    return path
