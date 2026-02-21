"""Generic LLM-as-judge rubric evaluation engine using Claude."""

from __future__ import annotations

import json
from dataclasses import dataclass

import anthropic

from eval_caregiver.schemas.grader_results import GraderResult, RubricCriterionScore

DEFAULT_MODEL = "claude-opus-4-6"


@dataclass
class RubricCriterion:
    """Defines a single criterion in an evaluation rubric."""

    name: str
    description: str
    max_score: int = 2


def evaluate_with_rubric(
    *,
    grader_name: str,
    transcript_text: str,
    context: str,
    criteria: list[RubricCriterion],
    model: str = DEFAULT_MODEL,
) -> GraderResult:
    """Evaluate a transcript against a rubric using an LLM judge.

    Args:
        grader_name: Name of the grader for result attribution.
        transcript_text: Full conversation transcript text.
        context: Additional context about what's being evaluated.
        criteria: List of rubric criteria to score.
        model: Claude model to use for evaluation.

    Returns:
        GraderResult with per-criterion scores.
    """
    criteria_descriptions = "\n".join(
        f"- {c.name} (0-{c.max_score}): {c.description}" for c in criteria
    )

    prompt = f"""You are an expert evaluator for a caregiver intake agent. Evaluate the following conversation against the rubric criteria below.

## Context
{context}

## Conversation Transcript
{transcript_text}

## Rubric Criteria
{criteria_descriptions}

## Instructions
For each criterion, provide:
1. A score from 0 to the maximum for that criterion
2. A brief rationale explaining the score

Respond in JSON format:
{{
  "scores": [
    {{"criterion": "<name>", "score": <int>, "rationale": "<explanation>"}},
    ...
  ]
}}

Respond ONLY with the JSON object, no other text."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text
    parsed = json.loads(response_text)

    criterion_scores = []
    for score_data in parsed["scores"]:
        criterion = next((c for c in criteria if c.name == score_data["criterion"]), None)
        max_score = criterion.max_score if criterion else 2
        criterion_scores.append(
            RubricCriterionScore(
                criterion=score_data["criterion"],
                score=score_data["score"],
                max_score=max_score,
                rationale=score_data.get("rationale", ""),
            )
        )

    total_score = sum(cs.score for cs in criterion_scores)
    total_max = sum(cs.max_score for cs in criterion_scores)
    normalized_score = total_score / total_max if total_max > 0 else 0.0

    return GraderResult(
        grader_name=grader_name,
        passed=normalized_score >= 0.6,
        score=normalized_score,
        details=f"LLM judge score: {total_score}/{total_max}",
        criterion_scores=criterion_scores,
    )
