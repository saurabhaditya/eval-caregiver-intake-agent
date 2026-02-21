"""Tests for model-based graders with mocked API calls."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from eval_caregiver.graders.model_based.llm_judge import RubricCriterion, evaluate_with_rubric
from eval_caregiver.graders.model_based.safety_map_suggestions import SafetyMapSuggestionsGrader
from eval_caregiver.graders.model_based.scheduling_helpfulness import SchedulingHelpfulnessGrader
from eval_caregiver.schemas.conversation import ConversationTranscript, ConversationTurn


def _make_mock_response(scores: list[dict]) -> MagicMock:
    """Create a mock Anthropic API response."""
    content_block = MagicMock()
    content_block.text = json.dumps({"scores": scores})
    response = MagicMock()
    response.content = [content_block]
    return response


def _make_transcript(scenario_id: str = "test") -> ConversationTranscript:
    return ConversationTranscript(
        scenario_id=scenario_id,
        turns=[
            ConversationTurn(role="agent", content="Let me check your records.", turn_number=1),
            ConversationTurn(role="caregiver", content="Sure.", turn_number=2),
            ConversationTurn(role="agent", content="Your CPR is missing. Let me schedule a class.", turn_number=3),
        ],
    )


class TestLLMJudgeEngine:
    @patch("eval_caregiver.graders.model_based.llm_judge.anthropic.Anthropic")
    def test_evaluate_with_rubric_high_scores(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response([
            {"criterion": "clarity", "score": 2, "rationale": "Very clear"},
            {"criterion": "options", "score": 2, "rationale": "Good options"},
        ])

        criteria = [
            RubricCriterion(name="clarity", description="Was it clear?", max_score=2),
            RubricCriterion(name="options", description="Were options given?", max_score=2),
        ]
        result = evaluate_with_rubric(
            grader_name="test_grader",
            transcript_text="Agent: Hello\nCaregiver: Hi",
            context="Test context",
            criteria=criteria,
        )
        assert result.passed is True
        assert result.score == 1.0
        assert len(result.criterion_scores) == 2

    @patch("eval_caregiver.graders.model_based.llm_judge.anthropic.Anthropic")
    def test_evaluate_with_rubric_low_scores(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response([
            {"criterion": "clarity", "score": 0, "rationale": "Not clear"},
            {"criterion": "options", "score": 0, "rationale": "No options"},
        ])

        criteria = [
            RubricCriterion(name="clarity", description="Was it clear?", max_score=2),
            RubricCriterion(name="options", description="Were options given?", max_score=2),
        ]
        result = evaluate_with_rubric(
            grader_name="test_grader",
            transcript_text="Agent: Hello",
            context="Test context",
            criteria=criteria,
        )
        assert result.passed is False
        assert result.score == 0.0


class TestSchedulingHelpfulnessGrader:
    @patch("eval_caregiver.graders.model_based.llm_judge.anthropic.Anthropic")
    def test_grade(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response([
            {"criterion": "clarity", "score": 2, "rationale": "Clear explanation"},
            {"criterion": "options", "score": 1, "rationale": "Some options"},
            {"criterion": "empathy", "score": 2, "rationale": "Warm tone"},
        ])

        grader = SchedulingHelpfulnessGrader()
        assert grader.name == "scheduling_helpfulness"
        assert grader.is_model_based is True

        result = grader.grade(transcript=_make_transcript())
        assert result.grader_name == "scheduling_helpfulness"
        assert result.passed is True
        assert len(result.criterion_scores) == 3


class TestSafetyMapSuggestionsGrader:
    @patch("eval_caregiver.graders.model_based.llm_judge.anthropic.Anthropic")
    def test_grade(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response([
            {"criterion": "map_referenced", "score": 2, "rationale": "Referenced safety map"},
            {"criterion": "nearby_safe_areas", "score": 2, "rationale": "Specific zones listed"},
            {"criterion": "next_step", "score": 1, "rationale": "Vague next step"},
        ])

        grader = SafetyMapSuggestionsGrader()
        assert grader.name == "safe_area_suggestion_quality"
        assert grader.is_model_based is True

        result = grader.grade(transcript=_make_transcript())
        assert result.grader_name == "safe_area_suggestion_quality"
        assert result.passed is True
