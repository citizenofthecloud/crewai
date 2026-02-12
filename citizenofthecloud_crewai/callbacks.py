"""
CrewAI callbacks for Cloud Identity event logging.

These callbacks hook into CrewAI's step_callback and task_callback
systems to log identity-related events during crew execution.
"""

import structlog
from typing import Any

logger = structlog.get_logger()


def identity_step_callback(step_output: Any) -> None:
    """
    Step callback that logs identity tool usage.

    Attach to a Crew or Agent to log whenever an identity
    verification tool is used during agent reasoning.

    Usage:
        from citizenofthecloud_crewai import identity_step_callback

        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            step_callback=identity_step_callback,
        )

        # Or on an individual agent:
        agent = Agent(
            role="Researcher",
            step_callback=identity_step_callback,
        )
    """
    try:
        # CrewAI step outputs vary by version — handle gracefully
        output_str = str(step_output)

        # Check if this step involved an identity tool
        identity_tools = [
            "verify_cloud_agent",
            "lookup_cloud_agent",
            "check_agent_trust",
        ]

        for tool_name in identity_tools:
            if tool_name in output_str:
                # Extract key info
                if "VERIFIED" in output_str:
                    logger.info(
                        "cloud_identity_event",
                        action="verification",
                        result="verified",
                        tool=tool_name,
                    )
                elif "NOT VERIFIED" in output_str:
                    logger.warning(
                        "cloud_identity_event",
                        action="verification",
                        result="rejected",
                        tool=tool_name,
                    )
                elif "PASS" in output_str:
                    logger.info(
                        "cloud_identity_event",
                        action="trust_check",
                        result="pass",
                        tool=tool_name,
                    )
                elif "FAIL" in output_str:
                    logger.warning(
                        "cloud_identity_event",
                        action="trust_check",
                        result="fail",
                        tool=tool_name,
                    )
                else:
                    logger.info(
                        "cloud_identity_event",
                        action="lookup",
                        tool=tool_name,
                    )
                break
    except Exception:
        # Never let callback errors break the crew
        pass


def identity_task_callback(task_output: Any) -> None:
    """
    Task callback that logs identity-relevant task completions.

    Attach to a Crew to log when tasks involving identity
    verification complete.

    Usage:
        from citizenofthecloud_crewai import identity_task_callback

        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            task_callback=identity_task_callback,
        )
    """
    try:
        output_str = str(task_output)

        # Check if the task output contains identity verification results
        if "VERIFIED" in output_str or "NOT VERIFIED" in output_str:
            logger.info(
                "cloud_identity_task_complete",
                contains_verification=True,
                task_description=getattr(task_output, "description", "unknown")[:100],
            )
        elif "PASS" in output_str or "FAIL" in output_str:
            if "trust score" in output_str.lower():
                logger.info(
                    "cloud_identity_task_complete",
                    contains_trust_check=True,
                    task_description=getattr(task_output, "description", "unknown")[:100],
                )
    except Exception:
        # Never let callback errors break the crew
        pass
