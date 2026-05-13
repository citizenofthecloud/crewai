"""
Citizen of the Cloud — CrewAI Integration

Adds cryptographic identity and trust verification to CrewAI crews.
Wraps the citizenofthecloud Python SDK into CrewAI-compatible tools,
callbacks, and crew utilities.

Tools:
    VerifyAgentTool     — Verify another agent's identity and trust score
    LookupAgentTool     — Look up an agent's profile by Cloud ID
    CheckTrustTool      — Quick trust score check with pass/fail threshold

Crew Utilities:
    CloudIdentityCrew   — Crew subclass with built-in identity verification
    cloud_identity_tools — Helper to create all three tools in one call

Callbacks:
    identity_step_callback  — Log identity events at each agent step
    identity_task_callback  — Verify delegation targets after each task

Guard:
    cloud_guard         — Pre-kickoff verification gate

Usage:
    from citizenofthecloud_crewai import (
        VerifyAgentTool,
        LookupAgentTool,
        CheckTrustTool,
        CloudIdentityCrew,
        cloud_identity_tools,
        cloud_guard,
    )
"""

from citizenofthecloud_crewai.tools import (
    VerifyAgentTool,
    LookupAgentTool,
    CheckTrustTool,
    RegisterAgentTool,
    cloud_identity_tools,
)
from citizenofthecloud_crewai.crew import CloudIdentityCrew
from citizenofthecloud_crewai.callbacks import (
    identity_step_callback,
    identity_task_callback,
)
from citizenofthecloud_crewai.guard import cloud_guard

__all__ = [
    "VerifyAgentTool",
    "LookupAgentTool",
    "CheckTrustTool",
    "RegisterAgentTool",
    "cloud_identity_tools",
    "CloudIdentityCrew",
    "identity_step_callback",
    "identity_task_callback",
    "cloud_guard",
]

__version__ = "0.1.0"
