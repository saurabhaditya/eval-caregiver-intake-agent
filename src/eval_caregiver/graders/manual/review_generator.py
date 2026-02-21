"""Generates review files for human labeling when manual review is flagged."""

from __future__ import annotations

import json
from pathlib import Path

from eval_caregiver.agent.base import AgentOutput
from eval_caregiver.schemas.grader_results import ScenarioResult
from eval_caregiver.schemas.scenarios import TestScenario


class ManualReviewGenerator:
    """Generates human-readable review files for scenarios that need manual review."""

    def __init__(self, output_dir: str = "output/reviews") -> None:
        self._output_dir = Path(output_dir)

    def generate(
        self,
        scenario: TestScenario,
        agent_output: AgentOutput,
        scenario_result: ScenarioResult,
    ) -> Path:
        """Generate a review file and return its path."""
        self._output_dir.mkdir(parents=True, exist_ok=True)

        review_data = {
            "scenario_id": scenario.scenario_id,
            "scenario_name": scenario.name,
            "scenario_description": scenario.description,
            "review_reasons": scenario_result.review_reasons,
            "transcript": [
                {"role": turn.role, "content": turn.content, "turn": turn.turn_number}
                for turn in agent_output.transcript.turns
            ],
            "grader_results": [
                {
                    "grader": gr.grader_name,
                    "passed": gr.passed,
                    "score": gr.score,
                    "details": gr.details,
                }
                for gr in scenario_result.grader_results
            ],
            "human_label": None,
            "human_notes": "",
        }

        filepath = self._output_dir / f"review_{scenario.scenario_id}.json"
        filepath.write_text(json.dumps(review_data, indent=2))
        return filepath
