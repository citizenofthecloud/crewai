"""
FastAPI route-guard middleware for serving CrewAI crews behind
Cloud Identity verification.

This is the framework's structural http-middleware: a FastAPI/Starlette
BaseHTTPMiddleware that verifies inbound X-Cloud-* headers before a
request reaches a crew.kickoff() handler. Companion to the in-process
`cloud_guard` function (which gates the same flow without FastAPI).
"""

from typing import Optional

try:
    from citizenofthecloud.fastapi import CloudGuard as _CloudGuard
    from citizenofthecloud.fastapi import cloud_guard_decorator as _decorator
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "FastAPI extras required. Install with: "
        "pip install 'citizenofthecloud[fastapi]'"
    ) from e

from citizenofthecloud import TrustPolicy


class CloudIdentityRouteGuard(_CloudGuard):
    """
    FastAPI route-guard middleware for CrewAI endpoints.

    Usage:
        from fastapi import FastAPI
        from citizenofthecloud_crewai import CloudIdentityRouteGuard
        from citizenofthecloud import TrustPolicy

        app = FastAPI()
        app.add_middleware(
            CloudIdentityRouteGuard,
            policy=TrustPolicy(minimum_trust_score=0.5),
            registry_url="https://citizenofthecloud.com",
        )
    """
    pass


def cloud_guard_route(policy: Optional[TrustPolicy] = None, **kwargs):
    """Decorator form for FastAPI routes that serve CrewAI crews."""
    return _decorator(policy=policy, **kwargs)
