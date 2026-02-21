"""Human-readable terminal scorecard output."""

from __future__ import annotations

from eval_caregiver.runner.quality_gates import QualityGateReport
from eval_caregiver.schemas.grader_results import ScenarioResult


def print_scorecard(results: list[ScenarioResult], gate_report: QualityGateReport) -> None:
    """Print a formatted scorecard to the terminal."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    needs_review = sum(1 for r in results if r.needs_manual_review)

    print()
    print("=" * 70)
    print("  CAREGIVER INTAKE AGENT EVALUATION SCORECARD")
    print("=" * 70)
    print()

    # Scenario results
    print(f"  Scenarios: {total} total, {passed} passed, {failed} failed")
    if needs_review:
        print(f"  Manual review needed: {needs_review}")
    print()
    print("-" * 70)

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        marker = "[+]" if result.passed else "[-]"
        print(f"  {marker} {result.scenario_name} ({result.scenario_id})")
        print(f"      Status: {status}  |  Score: {result.overall_score:.2f}")

        for gr in result.grader_results:
            gr_status = "pass" if gr.passed else "FAIL"
            print(f"      - {gr.grader_name}: {gr_status} ({gr.score:.2f})")
            if gr.criterion_scores:
                for cs in gr.criterion_scores:
                    print(f"        {cs.criterion}: {cs.score}/{cs.max_score}")

        if result.needs_manual_review:
            print(f"      >> Manual review: {', '.join(result.review_reasons)}")
        print()

    # Quality gates
    print("-" * 70)
    print("  QUALITY GATES")
    print("-" * 70)
    for gr in gate_report.gate_results:
        status = "PASS" if gr.passed else "FAIL"
        marker = "[+]" if gr.passed else "[-]"
        print(f"  {marker} {gr.gate.metric}")
        print(f"      Threshold: {gr.gate.threshold:.2f}  |  Actual: {gr.actual_value:.4f}  |  {status}")

    print()
    print("-" * 70)
    overall = "PASS" if gate_report.all_passed else "FAIL"
    print(f"  OVERALL: {overall}")
    print("=" * 70)
    print()
