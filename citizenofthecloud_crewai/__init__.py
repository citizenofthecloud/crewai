"""
Citizen of the Cloud — CrewAI Integration

Cryptographic identity and trust verification for CrewAI crews.

Tool surface — 20 items (17 agent-callable + 3 structural primitives):

Agent-callable BaseTool subclasses (17):
    LookupAgentTool, GetServerIdentityTool, ListDirectoryTool,
    GovernanceFeedTool, VerifyAgentTool, VerifyRequestTool,
    RequestChallengeTool, RespondToChallengeTool, SignChallengeTool,
    ProveIdentityTool, SignHeadersTool, SignRequestTool, CloudFetchTool,
    GenerateKeypairTool, RegisterAgentTool, ReportAgentTool, CheckTrustTool

Structural primitives (3):
    18. CloudIdentityRouteGuard / cloud_guard_route — FastAPI route-guard middleware
        (with cloud_guard as the in-process gate equivalent)
    19. CloudIdentityCrew — Crew subclass with built-in identity (framework-native)
    20. identity_step_callback / identity_task_callback — observability callbacks
"""

from citizenofthecloud_crewai.tools import (
    # Agent-callable tools (17)
    LookupAgentTool,
    GetServerIdentityTool,
    ListDirectoryTool,
    GovernanceFeedTool,
    VerifyAgentTool,
    VerifyRequestTool,
    RequestChallengeTool,
    RespondToChallengeTool,
    SignChallengeTool,
    ProveIdentityTool,
    SignHeadersTool,
    SignRequestTool,
    CloudFetchTool,
    GenerateKeypairTool,
    RegisterAgentTool,
    ReportAgentTool,
    CheckTrustTool,
    cloud_identity_tools,
)
from citizenofthecloud_crewai.crew import CloudIdentityCrew
from citizenofthecloud_crewai.callbacks import (
    identity_step_callback,
    identity_task_callback,
)
from citizenofthecloud_crewai.guard import cloud_guard
from citizenofthecloud_crewai.http import CloudIdentityHTTPClient
from citizenofthecloud_crewai.http_middleware import (
    CloudIdentityRouteGuard,
    cloud_guard_route,
)

__all__ = [
    # Agent-callable tools (17)
    "LookupAgentTool",
    "GetServerIdentityTool",
    "ListDirectoryTool",
    "GovernanceFeedTool",
    "VerifyAgentTool",
    "VerifyRequestTool",
    "RequestChallengeTool",
    "RespondToChallengeTool",
    "SignChallengeTool",
    "ProveIdentityTool",
    "SignHeadersTool",
    "SignRequestTool",
    "CloudFetchTool",
    "GenerateKeypairTool",
    "RegisterAgentTool",
    "ReportAgentTool",
    "CheckTrustTool",
    # Structural primitives (3)
    "CloudIdentityRouteGuard",      # 18 — http-middleware
    "cloud_guard_route",            # 18 — http-middleware (decorator form)
    "CloudIdentityCrew",            # 19 — framework-native gate
    "identity_step_callback",       # 20 — observability callbacks
    "identity_task_callback",       # 20 — observability callbacks
    # Helpers
    "cloud_identity_tools",
    "cloud_guard",                  # in-process equivalent of the route-guard
    "CloudIdentityHTTPClient",
]

__version__ = "0.2.0"
