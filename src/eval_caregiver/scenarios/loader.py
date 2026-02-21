"""Scenario loader: registry of all scenario collections loaded from JSON."""

from __future__ import annotations

import json
from pathlib import Path

from eval_caregiver.schemas.scenarios import ScenarioCollection, TestScenario

_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _load_collections() -> dict[str, ScenarioCollection]:
    """Scan data/scenarios/*.json and validate each as a ScenarioCollection."""
    collections: dict[str, ScenarioCollection] = {}
    scenarios_dir = _DATA_DIR / "scenarios"
    for path in sorted(scenarios_dir.glob("*.json")):
        raw = json.loads(path.read_text())
        collection = ScenarioCollection.model_validate(raw)
        collections[collection.collection_id] = collection
    return collections


_COLLECTIONS: dict[str, ScenarioCollection] = _load_collections()


def get_all_collections() -> list[ScenarioCollection]:
    """Return all registered scenario collections."""
    return list(_COLLECTIONS.values())


def get_collection(collection_id: str) -> ScenarioCollection:
    """Return a specific scenario collection by ID."""
    if collection_id not in _COLLECTIONS:
        raise ValueError(
            f"Unknown collection: {collection_id!r}. "
            f"Available: {sorted(_COLLECTIONS.keys())}"
        )
    return _COLLECTIONS[collection_id]


def get_all_scenarios() -> list[TestScenario]:
    """Return all scenarios across all collections."""
    scenarios = []
    for collection in _COLLECTIONS.values():
        scenarios.extend(collection.scenarios)
    return scenarios


def get_scenario(scenario_id: str) -> TestScenario:
    """Find a specific scenario by ID across all collections."""
    for collection in _COLLECTIONS.values():
        for scenario in collection.scenarios:
            if scenario.scenario_id == scenario_id:
                return scenario
    raise ValueError(
        f"Unknown scenario: {scenario_id!r}. "
        f"Available: {sorted(s.scenario_id for s in get_all_scenarios())}"
    )
