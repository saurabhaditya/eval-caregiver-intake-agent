"""Tests for the scenario loader and JSON data integrity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval_caregiver.scenarios.loader import (
    _DATA_DIR,
    get_all_collections,
    get_all_scenarios,
    get_collection,
    get_scenario,
)
from eval_caregiver.schemas.scenarios import ScenarioCollection, TestScenario


class TestDataDirectory:
    """Verify the data directory is correctly resolved and populated."""

    def test_data_dir_exists(self):
        assert _DATA_DIR.is_dir(), f"data/ directory not found at {_DATA_DIR}"

    def test_scenarios_dir_exists(self):
        assert (_DATA_DIR / "scenarios").is_dir()

    def test_responses_dir_exists(self):
        assert (_DATA_DIR / "responses").is_dir()

    def test_scenario_json_files_exist(self):
        files = list((_DATA_DIR / "scenarios").glob("*.json"))
        assert len(files) >= 2, f"Expected at least 2 scenario files, found {len(files)}"

    def test_response_json_files_exist(self):
        files = list((_DATA_DIR / "responses").glob("*.json"))
        assert len(files) >= 5, f"Expected at least 5 response files, found {len(files)}"


class TestScenarioJsonValidity:
    """Verify each scenario JSON file is valid and can be parsed by Pydantic."""

    def test_all_scenario_files_are_valid_json(self):
        for path in sorted((_DATA_DIR / "scenarios").glob("*.json")):
            raw = json.loads(path.read_text())
            assert isinstance(raw, dict), f"{path.name} is not a JSON object"

    def test_all_scenario_files_validate_as_collections(self):
        for path in sorted((_DATA_DIR / "scenarios").glob("*.json")):
            raw = json.loads(path.read_text())
            collection = ScenarioCollection.model_validate(raw)
            assert collection.collection_id, f"{path.name} has empty collection_id"
            assert collection.name, f"{path.name} has empty name"
            assert len(collection.scenarios) > 0, f"{path.name} has no scenarios"

    def test_scenario_ids_are_unique_globally(self):
        all_ids = [s.scenario_id for s in get_all_scenarios()]
        assert len(all_ids) == len(set(all_ids)), f"Duplicate scenario IDs: {all_ids}"

    def test_collection_ids_are_unique(self):
        collections = get_all_collections()
        ids = [c.collection_id for c in collections]
        assert len(ids) == len(set(ids)), f"Duplicate collection IDs: {ids}"

    def test_scenario_collection_backreference(self):
        """Each scenario's .collection field matches its parent collection_id."""
        for collection in get_all_collections():
            for scenario in collection.scenarios:
                assert scenario.collection == collection.collection_id, (
                    f"Scenario {scenario.scenario_id} has collection={scenario.collection!r} "
                    f"but is in collection {collection.collection_id!r}"
                )

    def test_filename_matches_collection_id(self):
        """JSON filename should match the collection_id inside."""
        for path in sorted((_DATA_DIR / "scenarios").glob("*.json")):
            raw = json.loads(path.read_text())
            assert path.stem == raw["collection_id"], (
                f"Filename {path.name} does not match collection_id {raw['collection_id']!r}"
            )


class TestResponseJsonValidity:
    """Verify each response JSON file has the correct structure."""

    def test_all_response_files_are_valid_json(self):
        for path in sorted((_DATA_DIR / "responses").glob("*.json")):
            raw = json.loads(path.read_text())
            assert isinstance(raw, dict), f"{path.name} is not a JSON object"

    def test_all_response_files_have_required_keys(self):
        required_keys = {"transcript", "intake_record", "action_log"}
        for path in sorted((_DATA_DIR / "responses").glob("*.json")):
            raw = json.loads(path.read_text())
            missing = required_keys - set(raw.keys())
            assert not missing, f"{path.name} missing keys: {missing}"

    def test_transcript_has_scenario_id_matching_filename(self):
        for path in sorted((_DATA_DIR / "responses").glob("*.json")):
            raw = json.loads(path.read_text())
            assert raw["transcript"]["scenario_id"] == path.stem, (
                f"{path.name}: transcript.scenario_id={raw['transcript']['scenario_id']!r} "
                f"does not match filename stem {path.stem!r}"
            )

    def test_action_log_has_scenario_id_matching_filename(self):
        for path in sorted((_DATA_DIR / "responses").glob("*.json")):
            raw = json.loads(path.read_text())
            assert raw["action_log"]["scenario_id"] == path.stem, (
                f"{path.name}: action_log.scenario_id != filename stem"
            )

    def test_transcripts_have_turns(self):
        for path in sorted((_DATA_DIR / "responses").glob("*.json")):
            raw = json.loads(path.read_text())
            turns = raw["transcript"]["turns"]
            assert len(turns) >= 2, f"{path.name} has fewer than 2 turns"

    def test_every_scenario_has_a_response(self):
        """Every scenario referenced in scenario collections should have a response file."""
        response_files = {p.stem for p in (_DATA_DIR / "responses").glob("*.json")}
        for scenario in get_all_scenarios():
            assert scenario.scenario_id in response_files, (
                f"No response file for scenario {scenario.scenario_id!r}"
            )


class TestGetAllCollections:
    def test_returns_list(self):
        result = get_all_collections()
        assert isinstance(result, list)

    def test_all_are_scenario_collections(self):
        for c in get_all_collections():
            assert isinstance(c, ScenarioCollection)

    def test_count_matches_json_files(self):
        json_count = len(list((_DATA_DIR / "scenarios").glob("*.json")))
        assert len(get_all_collections()) == json_count


class TestGetCollection:
    def test_known_collection(self):
        c = get_collection("compliance_missing_cases")
        assert c.collection_id == "compliance_missing_cases"
        assert len(c.scenarios) == 3

    def test_unknown_collection_raises(self):
        with pytest.raises(ValueError, match="Unknown collection"):
            get_collection("nonexistent_collection")

    def test_error_lists_available(self):
        with pytest.raises(ValueError, match="compliance_missing_cases"):
            get_collection("nonexistent_collection")


class TestGetAllScenarios:
    def test_returns_flat_list(self):
        scenarios = get_all_scenarios()
        assert isinstance(scenarios, list)
        assert all(isinstance(s, TestScenario) for s in scenarios)

    def test_count_matches_sum_of_collections(self):
        total = sum(len(c.scenarios) for c in get_all_collections())
        assert len(get_all_scenarios()) == total


class TestGetScenario:
    def test_known_scenario(self):
        s = get_scenario("compliance_cpr_missing")
        assert s.scenario_id == "compliance_cpr_missing"
        assert s.name == "CPR Certification Missing"

    def test_scenario_from_different_collection(self):
        s = get_scenario("geo_over_restricted")
        assert s.collection == "geo_over_restriction_cases"

    def test_unknown_scenario_raises(self):
        with pytest.raises(ValueError, match="Unknown scenario"):
            get_scenario("nonexistent_scenario")

    def test_error_lists_available(self):
        with pytest.raises(ValueError, match="compliance_cpr_missing"):
            get_scenario("nonexistent_scenario")
