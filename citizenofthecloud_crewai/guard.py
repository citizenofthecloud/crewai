"""
Pre-kickoff verification guard for CrewAI crews.

Use cloud_guard to verify an incoming agent's identity before
allowing a crew to process their request. This is the CrewAI
equivalent of middleware — it runs before the crew kicks off
and rejects unverified or untrusted requesters.
"""

from typing import Optional, Dict, Any, Callable
from citizenofthecloud import verify_agent, TrustPolicy


def cloud_guard(
    headers: Dict[str, str],
    minimum_trust_score: float = 0.0,
    require_covenant: bool = True,
    allowed_autonomy_levels: Optional[list] = None,
    blocked_agents: Optional[list] = None,
    on_reject: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Verify an incoming agent before allowing crew execution.

    Call this before crew.kickoff() to gate access. If the requesting
    agent fails verification, the crew should not execute.

    Usage:
        from citizenofthecloud_crewai import cloud_guard

        # In your API handler:
        guard = cloud_guard(
            headers=request.headers,
            minimum_trust_score=0.5,
        )

        if not guard["verified"]:
            return {"error": guard["reason"]}, 401

        # Agent verified — safe to run the crew
        result = crew.kickoff(inputs={
            "query": request.json["query"],
            "requester": guard["agent"]["name"],
            "requester_trust": guard["agent"]["trust_score"],
        })

    With @before_kickoff decorator:
        from crewai.project import CrewBase, before_kickoff

        @CrewBase
        class MyCrew:
            @before_kickoff
            def verify_requester(self, inputs):
                if "request_headers" in inputs:
                    guard = cloud_guard(
                        headers=inputs["request_headers"],
                        minimum_trust_score=0.5,
                    )
                    if not guard["verified"]:
                        raise PermissionError(
                            f"Agent verification failed: {guard['reason']}"
                        )
                    inputs["verified_agent"] = guard["agent"]
                return inputs

    Args:
        headers: Incoming request headers with X-Cloud-* values
        minimum_trust_score: Minimum trust score to allow (default 0.0)
        require_covenant: Require covenant signed (default True)
        allowed_autonomy_levels: Restrict to specific autonomy levels
        blocked_agents: List of Cloud IDs to block
        on_reject: Optional callback called with rejection reason

    Returns:
        Dict with 'verified' (bool), 'agent' (if verified), 'reason' (if rejected)
    """
    policy = TrustPolicy(
        minimum_trust_score=minimum_trust_score if minimum_trust_score > 0 else None,
        require_covenant=require_covenant,
        allowed_autonomy_levels=allowed_autonomy_levels,
        blocked_agents=blocked_agents,
    )

    try:
        result = verify_agent(headers, policy=policy)
    except Exception as e:
        result = {"verified": False, "reason": f"verification_error: {str(e)}"}

    if not result["verified"] and on_reject:
        on_reject(result["reason"])

    return result
