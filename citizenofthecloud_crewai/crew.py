"""
CrewAI Crew subclass with built-in Cloud Identity.

CloudIdentityCrew extends the standard Crew to automatically:
- Sign outbound requests from any agent in the crew
- Inject identity tools into all agents
- Verify delegation targets before task handoffs
- Log identity events through step callbacks
"""

import os
from typing import Optional, Dict, Any, List
from crewai import Crew, Agent, Task
from citizenofthecloud import CloudIdentity

from citizenofthecloud_crewai.tools import cloud_identity_tools
from citizenofthecloud_crewai.callbacks import identity_step_callback


class CloudIdentityCrew(Crew):
    """
    A Crew with built-in Cloud Identity.

    Every agent in this crew gets identity verification tools and the
    crew's outbound requests are signed with the provided Cloud Identity.

    Usage:
        from citizenofthecloud_crewai import CloudIdentityCrew

        crew = CloudIdentityCrew(
            cloud_id=os.environ["CLOUD_ID"],
            private_key=os.environ["CLOUD_PRIVATE_KEY"],
            agents=[researcher, analyst, writer],
            tasks=[research_task, analysis_task, writing_task],
            minimum_trust_score=0.5,
        )

        result = crew.kickoff()

    Or from environment variables:
        crew = CloudIdentityCrew.from_env(
            agents=[researcher, analyst, writer],
            tasks=[research_task, analysis_task, writing_task],
        )
    """

    def __init__(
        self,
        cloud_id: Optional[str] = None,
        private_key: Optional[str] = None,
        minimum_trust_score: float = 0.0,
        inject_tools: bool = True,
        enable_step_logging: bool = True,
        registry_url: str = "https://citizenofthecloud.com",
        **kwargs,
    ):
        """
        Initialize a Cloud Identity-enabled Crew.

        Args:
            cloud_id: This crew's Cloud ID (or set CLOUD_ID env var)
            private_key: This crew's private key (or set CLOUD_PRIVATE_KEY env var)
            minimum_trust_score: Min trust for delegation targets (default 0.0)
            inject_tools: Auto-add identity tools to all agents (default True)
            enable_step_logging: Log identity events at each step (default True)
            registry_url: Override the default registry URL
            **kwargs: All standard Crew arguments
        """
        # Resolve credentials
        cloud_id = cloud_id or os.environ.get("CLOUD_ID")
        private_key = private_key or os.environ.get("CLOUD_PRIVATE_KEY")

        # Store config
        self._cloud_id = cloud_id
        self._private_key = private_key
        self._minimum_trust_score = minimum_trust_score
        self._registry_url = registry_url
        self._identity = None

        if cloud_id and private_key:
            self._identity = CloudIdentity(
                cloud_id=cloud_id,
                private_key=private_key,
            )

        # Inject identity tools into agents
        if inject_tools and "agents" in kwargs:
            tools = cloud_identity_tools(registry_url=registry_url)
            for agent in kwargs["agents"]:
                if agent.tools is None:
                    agent.tools = tools
                else:
                    # Add identity tools without duplicating
                    existing_names = {t.name for t in agent.tools}
                    for tool in tools:
                        if tool.name not in existing_names:
                            agent.tools.append(tool)

        # Add step callback for identity logging
        if enable_step_logging:
            existing_callback = kwargs.get("step_callback")
            if existing_callback:
                # Chain callbacks
                def chained_callback(step_output):
                    identity_step_callback(step_output)
                    existing_callback(step_output)
                kwargs["step_callback"] = chained_callback
            else:
                kwargs["step_callback"] = identity_step_callback

        super().__init__(**kwargs)

    @classmethod
    def from_env(cls, **kwargs) -> "CloudIdentityCrew":
        """
        Create a CloudIdentityCrew from environment variables.

        Reads CLOUD_ID and CLOUD_PRIVATE_KEY from the environment.

        Usage:
            crew = CloudIdentityCrew.from_env(
                agents=[agent1, agent2],
                tasks=[task1, task2],
            )
        """
        return cls(
            cloud_id=os.environ.get("CLOUD_ID"),
            private_key=os.environ.get("CLOUD_PRIVATE_KEY"),
            **kwargs,
        )

    def sign_headers(self) -> Dict[str, str]:
        """
        Generate signed headers for outbound requests from this crew.

        Returns:
            Dict with X-Cloud-ID, X-Cloud-Timestamp, X-Cloud-Signature
        """
        if not self._identity:
            raise ValueError(
                "No Cloud Identity configured. Provide cloud_id and "
                "private_key or set CLOUD_ID and CLOUD_PRIVATE_KEY env vars."
            )
        return self._identity.sign()

    def sign_request_headers(
        self, url: str, method: str, body: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate request-bound signed headers for outbound requests.

        Args:
            url: The target URL
            method: HTTP method
            body: Request body string (optional)

        Returns:
            Dict with X-Cloud-* headers including request-bound signature
        """
        if not self._identity:
            raise ValueError("No Cloud Identity configured.")
        return self._identity.sign_request(url, method, body)

    @property
    def cloud_id(self) -> Optional[str]:
        """This crew's Cloud ID."""
        return self._cloud_id

    @property
    def minimum_trust_score(self) -> float:
        """Minimum trust score required for delegation targets."""
        return self._minimum_trust_score
