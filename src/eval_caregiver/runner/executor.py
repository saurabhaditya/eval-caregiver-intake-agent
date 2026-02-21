"""Evaluation executor: orchestrates agent → graders → results."""

from __future__ import annotations

from eval_caregiver.agent.base import AgentBase
from eval_caregiver.graders.base import Grader
from eval_caregiver.graders.manual.review_generator import ManualReviewGenerator
from eval_caregiver.schemas.grader_results import ScenarioResult
from eval_caregiver.schemas.scenarios import TestScenario


class EvalExecutor:
    """Runs scenarios through an agent and grades the outputs."""

    def __init__(
        self,
        agent: AgentBase,
        graders: dict[str, Grader],
        *,
        skip_model_graders: bool = False,
        review_generator: ManualReviewGenerator | None = None,
    ) -> None:
        self._agent = agent
        self._graders = graders
        self._skip_model_graders = skip_model_graders
        self._review_generator = review_generator

    def run_scenario(self, scenario: TestScenario) -> ScenarioResult:
        """Run a single scenario and return the result."""
        output = self._agent.run_scenario(scenario)

        grader_results = []
        for grader_name in scenario.grader_names:
            grader = self._graders.get(grader_name)
            if grader is None:
                continue
            if self._skip_model_graders and grader.is_model_based:
                continue

            result = grader.grade(
                scenario=scenario,
                transcript=output.transcript,
                intake_record=output.intake_record,
                action_log=output.action_log,
            )
            grader_results.append(result)

        all_passed = all(r.passed for r in grader_results) if grader_results else True

        # Check if manual review is needed
        review_reasons: list[str] = []
        if grader_results:
            failing = [r for r in grader_results if not r.passed]
            if failing:
                review_reasons.append(f"{len(failing)} grader(s) failed: {[r.grader_name for r in failing]}")
            # Flag disagreements between code and model graders
            code_results = [r for r in grader_results if not self._graders[r.grader_name].is_model_based]
            model_results = [r for r in grader_results if self._graders[r.grader_name].is_model_based]
            if code_results and model_results:
                code_pass = all(r.passed for r in code_results)
                model_pass = all(r.passed for r in model_results)
                if code_pass != model_pass:
                    review_reasons.append("Disagreement between code-based and model-based graders")

        needs_review = len(review_reasons) > 0

        scenario_result = ScenarioResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            grader_results=grader_results,
            passed=all_passed,
            needs_manual_review=needs_review,
            review_reasons=review_reasons,
        )

        if needs_review and self._review_generator:
            self._review_generator.generate(scenario, output, scenario_result)

        return scenario_result

    def run_scenarios(self, scenarios: list[TestScenario]) -> list[ScenarioResult]:
        """Run multiple scenarios and return all results."""
        return [self.run_scenario(s) for s in scenarios]
