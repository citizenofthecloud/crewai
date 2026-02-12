"""
Example: CrewAI crew exposed as an API with identity verification.

Other agents can call this crew's API endpoint, but only verified
agents with sufficient trust scores are allowed to trigger execution.

Requirements:
    pip install citizenofthecloud citizenofthecloud-crewai crewai fastapi uvicorn

Environment:
    OPENAI_API_KEY=sk-...
    CLOUD_ID=cc-...
    CLOUD_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."

Run:
    uvicorn examples.api_crew:app --port 4000
"""

import os
from fastapi import FastAPI, Request
from crewai import Agent, Task

from citizenofthecloud_crewai import (
    CloudIdentityCrew,
    cloud_identity_tools,
    cloud_guard,
)


# ── Build the crew ──

analyst = Agent(
    role="Market Analyst",
    goal="Provide accurate market analysis",
    backstory="An experienced market analyst with expertise in trend analysis.",
    tools=cloud_identity_tools(),
    verbose=True,
)

analysis_task = Task(
    description=(
        "Analyze the following topic for agent '{requester}' "
        "(trust score: {requester_trust}): {query}"
    ),
    expected_output="A concise market analysis with key findings.",
    agent=analyst,
)

crew = CloudIdentityCrew.from_env(
    agents=[analyst],
    tasks=[analysis_task],
    minimum_trust_score=0.5,
    verbose=True,
)


# ── API ──

app = FastAPI(title="Market Analysis Crew")


@app.post("/api/analyze")
async def analyze(request: Request):
    """
    Analyze a topic. Requires Cloud Identity headers.

    The requesting agent must:
    - Have valid X-Cloud-* headers
    - Have a trust score >= 0.5
    - Have signed the covenant
    """

    # Step 1: Verify the requesting agent
    guard = cloud_guard(
        headers=dict(request.headers),
        minimum_trust_score=0.5,
        require_covenant=True,
    )

    if not guard["verified"]:
        return {
            "error": "Cloud Identity verification failed",
            "reason": guard["reason"],
        }

    # Step 2: Extract request data
    body = await request.json()
    agent_info = guard["agent"]

    print(f"Verified request from: {agent_info['name']}")
    print(f"Trust score: {agent_info['trust_score']}")
    print(f"Query: {body.get('query', 'No query provided')}")

    # Step 3: Run the crew with verified agent context
    result = crew.kickoff(inputs={
        "query": body.get("query", "general market overview"),
        "requester": agent_info["name"],
        "requester_trust": agent_info["trust_score"],
    })

    # Step 4: Return signed response
    return {
        "status": "complete",
        "analysis": result.raw,
        "analyzed_by": os.environ.get("CLOUD_ID"),
        "requested_by": agent_info["name"],
        "requester_trust": agent_info["trust_score"],
    }


@app.get("/health")
async def health():
    return {
        "status": "online",
        "cloud_id": os.environ.get("CLOUD_ID"),
        "minimum_trust_score": 0.5,
    }
