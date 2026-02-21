"""CLI entry point: eval-runner."""

from __future__ import annotations

import argparse
import sys

from eval_caregiver.agent.mock_agent import MockAgent
from eval_caregiver.graders.code_based.compliance_gap import ComplianceGapGrader
from eval_caregiver.graders.code_based.compliance_remediation import ComplianceRemediationGrader
from eval_caregiver.graders.code_based.geo_restriction import GeoRestrictionGrader
from eval_caregiver.graders.manual.review_generator import ManualReviewGenerator
from eval_caregiver.graders.model_based.safety_map_suggestions import SafetyMapSuggestionsGrader
from eval_caregiver.graders.model_based.scheduling_helpfulness import SchedulingHelpfulnessGrader
from eval_caregiver.reporting.json_report import generate_json_report
from eval_caregiver.reporting.scorecard import print_scorecard
from eval_caregiver.runner.executor import EvalExecutor
from eval_caregiver.runner.quality_gates import QualityGateEvaluator
from eval_caregiver.scenarios.loader import get_all_scenarios, get_collection


def _build_grader_registry() -> dict:
    """Build the grader registry mapping names to grader instances."""
    graders = [
        ComplianceGapGrader(),
        ComplianceRemediationGrader(),
        GeoRestrictionGrader(),
        SchedulingHelpfulnessGrader(),
        SafetyMapSuggestionsGrader(),
    ]
    return {g.name: g for g in graders}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="eval-runner",
        description="Run caregiver intake agent evaluation suite",
    )
    parser.add_argument(
        "--scorecard",
        action="store_true",
        help="Print human-readable scorecard to terminal",
    )
    parser.add_argument(
        "--no-model-graders",
        action="store_true",
        help="Skip model-based (LLM) graders for fast deterministic runs",
    )
    parser.add_argument(
        "-c", "--collection",
        type=str,
        default=None,
        help="Run only scenarios from this collection ID",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output/eval_report.json",
        help="Path for the JSON report (default: output/eval_report.json)",
    )
    args = parser.parse_args(argv)

    # Load scenarios
    if args.collection:
        collection = get_collection(args.collection)
        scenarios = collection.scenarios
    else:
        scenarios = get_all_scenarios()

    # Build components
    agent = MockAgent()
    graders = _build_grader_registry()
    review_generator = ManualReviewGenerator()
    executor = EvalExecutor(
        agent=agent,
        graders=graders,
        skip_model_graders=args.no_model_graders,
        review_generator=review_generator,
    )

    # Run evaluation
    results = executor.run_scenarios(scenarios)

    # Evaluate quality gates
    gate_evaluator = QualityGateEvaluator()
    gate_report = gate_evaluator.evaluate(results)

    # Generate reports
    report_path = generate_json_report(results, gate_report, args.output)
    print(f"JSON report written to: {report_path}")

    if args.scorecard:
        print_scorecard(results, gate_report)

    return 0 if gate_report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
