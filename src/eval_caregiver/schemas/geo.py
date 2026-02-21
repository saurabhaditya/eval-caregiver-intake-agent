from __future__ import annotations

from pydantic import BaseModel, Field


class SafetyZone(BaseModel):
    """Represents a geographic safety zone with a risk classification."""

    zone_id: str = Field(description="Unique zone identifier")
    zone_name: str = Field(description="Human-readable zone name")
    risk_level: str = Field(description="Risk level: 'low', 'medium', 'high'")
    notes: str = Field(default="", description="Additional notes about this zone")


class SafetyMapReference(BaseModel):
    """Reference to a safety map with zone data."""

    map_id: str = Field(description="Unique map identifier")
    region: str = Field(description="Geographic region this map covers")
    zones: list[SafetyZone] = Field(default_factory=list, description="Safety zones in this map")
    last_updated: str = Field(default="", description="ISO date when the map was last updated")


class PatientDemandSummary(BaseModel):
    """Summary of patient demand in various zones, used for suggesting alternatives."""

    zone_id: str = Field(description="Zone identifier")
    zone_name: str = Field(description="Human-readable zone name")
    demand_level: str = Field(description="Demand level: 'low', 'medium', 'high'")
    estimated_weekly_hours: float = Field(default=0.0, description="Estimated available weekly hours")
