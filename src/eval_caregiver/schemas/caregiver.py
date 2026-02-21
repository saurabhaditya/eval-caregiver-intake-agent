from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class ComplianceRecord(BaseModel):
    """Tracks compliance items for a caregiver (certifications, background checks, etc.)."""

    item_name: str = Field(description="Name of the compliance item, e.g. 'CPR Certification'")
    status: str = Field(description="Status: 'valid', 'expired', 'missing', 'unknown'")
    expiration_date: date | None = Field(default=None, description="Expiration date if applicable")
    notes: str = Field(default="", description="Additional notes about this compliance item")


class GeoPreferences(BaseModel):
    """Geographic preferences and restrictions for a caregiver."""

    preferred_zones: list[str] = Field(default_factory=list, description="Zone IDs the caregiver prefers")
    excluded_zones: list[str] = Field(default_factory=list, description="Zone IDs the caregiver refuses")
    max_travel_minutes: int | None = Field(default=None, description="Maximum travel time in minutes")
    has_own_transport: bool = Field(default=False, description="Whether the caregiver has their own transportation")


class CaregiverProfile(BaseModel):
    """Core profile information for a caregiver."""

    caregiver_id: str = Field(description="Unique identifier for the caregiver")
    full_name: str = Field(description="Full legal name")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    years_experience: int = Field(default=0, description="Years of caregiving experience")
    specialties: list[str] = Field(default_factory=list, description="Areas of specialty")
    compliance: list[ComplianceRecord] = Field(default_factory=list, description="Compliance records")
    geo_preferences: GeoPreferences = Field(default_factory=GeoPreferences, description="Geographic preferences")


class StructuredIntakeRecord(BaseModel):
    """The structured output from a caregiver intake conversation."""

    caregiver: CaregiverProfile = Field(description="The caregiver profile extracted from intake")
    compliance_gaps: list[str] = Field(
        default_factory=list, description="Identified compliance gaps (items missing or expired)"
    )
    remediation_actions: list[str] = Field(
        default_factory=list, description="Actions offered to address compliance gaps"
    )
    geo_concerns: list[str] = Field(
        default_factory=list, description="Geographic concerns identified during intake"
    )
    safe_area_suggestions: list[str] = Field(
        default_factory=list, description="Safe area suggestions provided to the caregiver"
    )
    overall_status: str = Field(
        default="incomplete", description="Overall intake status: 'complete', 'incomplete', 'needs_review'"
    )
