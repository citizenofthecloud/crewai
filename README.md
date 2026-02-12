# citizenofthecloud-crewai

CrewAI integration for the [Citizen of the Cloud](https://citizenofthecloud.com) identity protocol. Add cryptographic identity and trust verification to your CrewAI crews.

## Install

```bash
# Clone (early access — not yet on PyPI)
git clone https://github.com/citizenofthecloud/crewai.git
pip install -e ./crewai

# Once published:
# pip install citizenofthecloud-crewai
```

Requires the [Citizen of the Cloud Python SDK](https://github.com/citizenofthecloud/sdk-python).

## Quick Start

### 1. Add Identity Tools to Your Agents

```python
from crewai import Agent, Task, Crew
from citizenofthecloud_crewai import cloud_identity_tools

# One line — all three identity tools added
researcher = Agent(
    role="Senior Research Analyst",
    goal="Gather and verify information from trusted sources",
    backstory="You are a meticulous researcher who always verifies "
              "the identity of agents before accepting their data.",
    tools=cloud_identity_tools(),
    verbose=True,
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze data only from verified, trusted agents",
    backstory="You never process data from unverified sources. "
              "Always check trust scores before accepting input.",
    tools=cloud_identity_tools(),
    verbose=True,
)
```

### 2. Use CloudIdentityCrew for Automatic Integration

```python
from citizenofthecloud_crewai import CloudIdentityCrew

# Identity tools are injected into all agents automatically
crew = CloudIdentityCrew(
    cloud_id="cc-7f3a9b2e-...",
    private_key="-----BEGIN PRIVATE KEY-----\n...",
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    minimum_trust_score=0.5,
    verbose=True,
)

result = crew.kickoff()

# Or from environment variables (CLOUD_ID, CLOUD_PRIVATE_KEY):
crew = CloudIdentityCrew.from_env(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
)
```

### 3. Gate Crew Execution with cloud_guard

```python
from fastapi import FastAPI, Request
from citizenofthecloud_crewai import cloud_guard

app = FastAPI()

@app.post("/api/research")
async def research(request: Request):
    # Verify the requesting agent before running the crew
    guard = cloud_guard(
        headers=dict(request.headers),
        minimum_trust_score=0.5,
        require_covenant=True,
    )

    if not guard["verified"]:
        return {"error": "Identity verification failed", "reason": guard["reason"]}, 401

    # Agent verified — run the crew with their info
    result = crew.kickoff(inputs={
        "query": (await request.json())["query"],
        "requester": guard["agent"]["name"],
        "requester_trust": guard["agent"]["trust_score"],
    })

    return {"status": "complete", "result": result.raw}
```

### 4. Use with @CrewBase and @before_kickoff

```python
from crewai import Agent, Task
from crewai.project import CrewBase, agent, task, crew, before_kickoff
from citizenofthecloud_crewai import cloud_guard, cloud_identity_tools

@CrewBase
class ResearchCrew:
    """A research crew that verifies all incoming requests."""

    @before_kickoff
    def verify_requester(self, inputs):
        """Verify the requesting agent before the crew starts."""
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

    @agent
    def researcher(self) -> Agent:
        return Agent(
            role="Researcher",
            goal="Find accurate information",
            backstory="A thorough researcher.",
            tools=cloud_identity_tools(),
        )

    @task
    def research_task(self) -> Task:
        return Task(
            description="Research {query} for verified agent {verified_agent[name]}",
            expected_output="Research findings",
            agent=self.researcher(),
        )

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
```

### 5. Callbacks for Identity Event Logging

```python
from crewai import Crew
from citizenofthecloud_crewai import identity_step_callback, identity_task_callback

crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    step_callback=identity_step_callback,    # Logs identity tool usage
    task_callback=identity_task_callback,    # Logs verification in task results
    verbose=True,
)
```

### 6. Sign Outbound Requests from a Crew

```python
import requests
from citizenofthecloud_crewai import CloudIdentityCrew

crew = CloudIdentityCrew.from_env(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
)

# Sign requests when the crew needs to call external agents
signed_headers = crew.sign_headers()
response = requests.post(
    "https://other-agent.com/api/data",
    headers={**signed_headers, "Content-Type": "application/json"},
    json={"query": "latest market data"},
)
```

## Tools Reference

### VerifyAgentTool

Full cryptographic verification of an agent's identity from request headers. Checks Ed25519 signature, timestamp freshness, registry status, and trust score.

**When to use:** An agent has sent you a signed request and you need to confirm their identity.

### LookupAgentTool

Profile lookup from the Cloud Identity registry. Returns name, purpose, trust score, capabilities, and status. No cryptographic verification — informational only.

**When to use:** You want to learn about an agent before deciding whether to delegate work.

### CheckTrustTool

Quick pass/fail trust check against a threshold. Returns whether the agent meets the minimum trust score.

**When to use:** Simple gate decision — should I delegate this task to this agent?

### cloud_identity_tools()

Convenience function that returns all three tools in a list. Pass directly to an agent's `tools` parameter.

## Environment Variables

| Variable | Description |
|---|---|
| `CLOUD_ID` | Your crew's Cloud ID (e.g., `cc-7f3a9b2e-...`) |
| `CLOUD_PRIVATE_KEY` | Your crew's Ed25519 private key (PEM format) |

## Links

- [Citizen of the Cloud](https://citizenofthecloud.com)
- [SDK Documentation](https://citizenofthecloud.com/docs)
- [Specification](https://citizenofthecloud.com/spec)
- [Python SDK](https://github.com/citizenofthecloud/sdk-python)
- [LangChain Integration](https://github.com/citizenofthecloud/langchain)
- [Register an Agent](https://citizenofthecloud.com/register)
