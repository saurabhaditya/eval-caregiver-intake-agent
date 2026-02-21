from __future__ import annotations

from pydantic import BaseModel, Field


class TestScenario(BaseModel):
    """Defines a single test scenario for the caregiver intake agent."""

    scenario_id: str = Field(description="Unique scenario identifier")
    name: str = Field(description="Human-readable scenario name")
    description: str = Field(description="Detailed description of what this scenario tests")
    collection: str = Field(description="Which collection this scenario belongs to")
    required: bool = Field(default=True, description="Whether this scenario must pass for the suite to pass")
    grader_names: list[str] = Field(description="Names of graders to apply to this scenario")
    caregiver_setup: dict = Field(
        default_factory=dict,
        description="Setup data for the caregiver profile in this scenario",
    )
    expected_compliance_gaps: list[str] = Field(
        default_factory=list,
        description="Compliance gaps the agent should identify",
    )
    expected_geo_concerns: list[str] = Field(
        default_factory=list,
        description="Geographic concerns the agent should flag",
    )


class ScenarioCollection(BaseModel):
    """A named collection of related test scenarios."""

    collection_id: str = Field(description="Unique collection identifier")
    name: str = Field(description="Human-readable collection name")
    description: str = Field(description="What this collection tests")
    scenarios: list[TestScenario] = Field(default_factory=list, description="Scenarios in this collection")
