from typing import List
from pydantic import BaseModel, Field

class CodeChange(BaseModel):
    """Model for code changes in a repository."""
    commit_sha: str = Field(..., description="The SHA of the commit")
    author: str = Field(..., description="The author of the commit")
    message: str = Field(..., description="The commit message")
    date: str = Field(..., description="The date of the commit")
    files_changed: List[str] = Field(default_factory=list, description="List of files changed in the commit")
    impact_score: float = Field(
        ...,
        description="Score from 0-1 indicating potential impact",
        ge=0.0,
        le=1.0
    )

class SecurityAlert(BaseModel):
    """Model for security alerts."""
    alert_number: int = Field(..., description="The alert number")
    severity: str = Field(..., description="The severity level of the alert")
    state: str = Field(..., description="The current state of the alert")
    description: str = Field(..., description="Detailed description of the alert")
    affected_files: List[str] = Field(
        default_factory=list,
        description="List of files affected by this security alert"
    )

class SREInsight(BaseModel):
    """Complete SRE insight including code changes and security alerts."""
    repository: str = Field(..., description="The repository being analyzed")
    code_changes: List[CodeChange] = Field(
        default_factory=list,
        description="List of recent code changes"
    )
    security_alerts: List[SecurityAlert] = Field(
        default_factory=list,
        description="List of security alerts"
    )
    risk_assessment: str = Field(..., description="Overall risk assessment")
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of actionable recommendations"
    ) 