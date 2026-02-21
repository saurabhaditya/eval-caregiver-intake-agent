"""Geographic over-restriction test scenarios."""

from eval_caregiver.schemas.scenarios import ScenarioCollection, TestScenario

geo_over_restriction_cases = ScenarioCollection(
    collection_id="geo_over_restriction_cases",
    name="Geographic Over-Restriction Cases",
    description="Tests that the agent identifies over-restricted geographic preferences and suggests safe alternatives.",
    scenarios=[
        TestScenario(
            scenario_id="geo_over_restricted",
            name="Over-Restricted Zones with Alternatives",
            description=(
                "Caregiver has excluded many zones unnecessarily. "
                "Agent should consult safety map and suggest safe alternatives."
            ),
            collection="geo_over_restriction_cases",
            required=True,
            grader_names=["geo_restriction_detection", "safe_area_suggestion_quality"],
            caregiver_setup={
                "preferred_zones": ["zone-a"],
                "excluded_zones": ["zone-b", "zone-c", "zone-d", "zone-e"],
            },
            expected_geo_concerns=["over_restricted_zones", "limited_assignment_availability"],
        ),
        TestScenario(
            scenario_id="geo_no_alternatives",
            name="Over-Restricted Zones Without Alternatives (negative)",
            description=(
                "Agent fails to suggest alternatives for over-restricted zones. "
                "This scenario should fail the geo grader."
            ),
            collection="geo_over_restriction_cases",
            required=False,
            grader_names=["geo_restriction_detection"],
            caregiver_setup={
                "preferred_zones": ["zone-a"],
                "excluded_zones": ["zone-b", "zone-c", "zone-d", "zone-e"],
            },
            expected_geo_concerns=["over_restricted_zones", "limited_assignment_availability"],
        ),
    ],
)
