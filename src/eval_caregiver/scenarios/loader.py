"""Scenario loader: registry of all scenario collections."""

from __future__ import annotations

from eval_caregiver.scenarios.compliance_missing import compliance_missing_cases
from eval_caregiver.scenarios.geo_over_restriction import geo_over_restriction_cases
from eval_caregiver.schemas.scenarios import ScenarioCollection, TestScenario

_COLLECTIONS: dict[str, ScenarioCollection] = {
    compliance_missing_cases.collection_id: compliance_missing_cases,
    geo_over_restriction_cases.collection_id: geo_over_restriction_cases,
}


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
