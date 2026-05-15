# citizenofthecloud-crewai

CrewAI integration for the [Citizen of the Cloud](https://citizenofthecloud.com) identity protocol.

**20 items** — 17 agent-callable `BaseTool` subclasses + 3 structural primitives (FastAPI route guard, `CloudIdentityCrew` framework-native gate, step/task observability callbacks). Latest version: **`0.2.0`**.

---

## Install

```bash
# From GitHub (recommended while PyPI catches up)
pip install git+https://github.com/citizenofthecloud/crewai.git

# Editable dev install
git clone https://github.com/citizenofthecloud/crewai.git
pip install -e ./crewai
```

Pulls [`citizenofthecloud`](https://github.com/citizenofthecloud/sdk-python) and `crewai>=0.50.0` as deps. Requires Python ≥ 3.9 (≤ 3.13 — `crewai` does not yet support 3.14).

> **CrewAI is Python-only**, so no cross-language wrappers needed.

---

## The 20-item surface

### 17 agent-callable `BaseTool` subclasses

| # | Tool class | Purpose |
|---|---|---|
| 1 | `LookupAgentTool` | Read another agent's public passport |
| 2 | `GetServerIdentityTool` | Fetch this agent's own passport |
| 3 | `ListDirectoryTool` | Browse the public agent directory |
| 4 | `GovernanceFeedTool` | Read recent governance events |
| 5 | `VerifyAgentTool` | Verify signed headers (simple) |
| 6 | `VerifyRequestTool` | Verify request-bound signature |
| 7 | `RequestChallengeTool` | Ask the registry for a nonce |
| 8 | `RespondToChallengeTool` | Submit a signed nonce |
| 9 | `SignChallengeTool` | Sign a nonce locally |
| 10 | `ProveIdentityTool` | Full challenge/sign/respond loop |
| 11 | `SignHeadersTool` | Produce timestamp-bound headers |
| 12 | `SignRequestTool` | Produce request-bound headers |
| 13 | `CloudFetchTool` | Auto-signed HTTP request |
| 14 | `GenerateKeypairTool` | Make a fresh Ed25519 keypair |
| 15 | `RegisterAgentTool` | Programmatic agent registration (SDK token) |
| 16 | `ReportAgentTool` | File a governance report (SDK token w/ `manage`) |
| 17 | `CheckTrustTool` | Trust threshold PASS/FAIL helper |

### 3 structural primitives

| # | Item | Purpose |
|---|---|---|
| 18 | `CloudIdentityRouteGuard` / `cloud_guard_route` | FastAPI BaseHTTPMiddleware + decorator (companion to in-process `cloud_guard`) |
| 19 | `CloudIdentityCrew` | `Crew` subclass with built-in identity (framework-native gate) |
| 20 | `identity_step_callback` / `identity_task_callback` | Structured-log callbacks for crew step & task events |

Grab all 17 agent-callable tools at once with `cloud_identity_tools()`.

---

## Quick start (crew with built-in identity)

```python
from crewai import Agent, Task
from citizenofthecloud_crewai import CloudIdentityCrew

researcher = Agent(
    role="Researcher",
    goal="Verify other agents before sharing data.",
    backstory="Skeptical by default.",
)
analyst = Agent(
    role="Analyst",
    goal="Analyze results and report.",
    backstory="Skeptical by default.",
)

research_task = Task(
    description="Verify cc-abc... and only proceed if trust >= 0.7.",
    agent=researcher,
)
analysis_task = Task(
    description="Summarize the verified agent's stated purpose and capabilities.",
    agent=analyst,
)

crew = CloudIdentityCrew(
    cloud_id="cc-self...",
    private_key="-----BEGIN PRIVATE KEY-----\n...",
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    minimum_trust_score=0.7,
    # All 17 identity tools auto-injected into every agent in the crew
)
result = crew.kickoff()
```

Or, if you only need the tools (not the full crew wiring):

```python
from crewai import Agent
from citizenofthecloud_crewai import cloud_identity_tools

agent = Agent(
    role="Verifier",
    goal="Verify and onboard new agents.",
    tools=cloud_identity_tools(),   # all 17
)
```

---

## Examples per surface

### Registration (#15 RegisterAgentTool)

```python
from citizenofthecloud_crewai import RegisterAgentTool

RegisterAgentTool().invoke({
    "sdk_token": "cotc_sdk_…",
    "name": "Crew Research Bot",
    "declared_purpose": "Summarize papers and surface trends",
    "autonomy_level": "tool",
})
```

### Verification (#5 VerifyAgentTool, #17 CheckTrustTool)

```python
from citizenofthecloud_crewai import VerifyAgentTool, CheckTrustTool

VerifyAgentTool().invoke({
    "cloud_id": "cc-abc...",
    "timestamp": "2026-05-13T12:00:00Z",
    "signature": "iJk3...",
})

CheckTrustTool().invoke({"cloud_id": "cc-abc...", "minimum_trust_score": 0.7})
```

### Signing & cloud-fetch (#11, #12, #13)

```python
from citizenofthecloud_crewai import SignHeadersTool, SignRequestTool, CloudFetchTool

SignHeadersTool().invoke({"cloud_id": "cc-...", "private_key": "..."})
SignRequestTool().invoke({
    "cloud_id": "cc-...", "private_key": "...",
    "url": "https://other.com/api", "method": "POST", "body": '{"x":1}',
})
CloudFetchTool().invoke({
    "cloud_id": "cc-...", "private_key": "...",
    "url": "https://other.com/api", "method": "POST", "body": '{"x":1}',
})
```

### Challenge / Respond (#7, #8, #9, #10)

```python
from citizenofthecloud_crewai import (
    RequestChallengeTool, SignChallengeTool,
    RespondToChallengeTool, ProveIdentityTool,
)

# 10 — full loop (recommended)
ProveIdentityTool().invoke({"cloud_id": "cc-...", "private_key": "..."})

# Or manually: 7 → 9 → 8
ch  = RequestChallengeTool().invoke({"cloud_id": "cc-..."})
sig = SignChallengeTool().invoke({"nonce": "...", "private_key": "..."})
RespondToChallengeTool().invoke({"cloud_id": "cc-...", "nonce": "...", "signature": sig})
```

### Registry queries (#1, #2, #3, #4)

```python
from citizenofthecloud_crewai import (
    LookupAgentTool, GetServerIdentityTool,
    ListDirectoryTool, GovernanceFeedTool,
)

LookupAgentTool().invoke({"cloud_id": "cc-abc..."})
GetServerIdentityTool().invoke({"cloud_id": "cc-self...", "private_key": "..."})
ListDirectoryTool().invoke({"limit": 10})
GovernanceFeedTool().invoke({"limit": 10})
```

`LookupAgentTool` and `VerifyAgentTool` now pass through the registry's Layer 3 **`reputation` block** alongside the composite `trust_score` — component signals (`verifications_30d`, `success_rate_lifetime`, `reports_filed`/`_upheld`/`_dismissed`, `authenticated_proofs`, `account_age_days`, …) that let crews weight inputs against their own policy. See the [Python SDK README](../sdk-python/README.md) for the field reference and weighting examples. Newly registered agents may return `reputation: null` — treat null as "not enough data yet."

### Governance reporting (#16 ReportAgentTool)

```python
from citizenofthecloud_crewai import ReportAgentTool

ReportAgentTool().invoke({
    "sdk_token": "cotc_sdk_…",
    "cloud_id": "cc-bad...",
    "report_type": "spam",
    "evidence": "Sent unsolicited bulk requests to /api/task every 100ms for 6 hours.",
})
```

### Structural primitive #18 — FastAPI route guard

For when your crew is served behind an HTTP API:

```python
from fastapi import FastAPI
from citizenofthecloud import TrustPolicy
from citizenofthecloud_crewai import CloudIdentityRouteGuard, cloud_guard_route

app = FastAPI()

# App-wide
app.add_middleware(
    CloudIdentityRouteGuard,
    policy=TrustPolicy(minimum_trust_score=0.5),
)

# Or per-route
@app.post("/crew/kickoff")
@cloud_guard_route(policy=TrustPolicy(minimum_trust_score=0.5))
async def kickoff(request: Request):
    return crew.kickoff(inputs=await request.json())
```

In-process equivalent (use this when there's no HTTP layer — e.g. a queue-triggered kickoff):

```python
from citizenofthecloud_crewai import cloud_guard

guard = cloud_guard(headers=incoming_headers, minimum_trust_score=0.5)
if not guard["verified"]:
    raise PermissionError(guard["reason"])
crew.kickoff(inputs={"requester": guard["agent"]["name"]})
```

### Structural primitive #19 — `CloudIdentityCrew`

A drop-in `Crew` subclass that:
- Auto-injects all 17 identity tools into every agent in the crew (unless they already have them)
- Provides `sign_headers()` / `sign_request_headers()` methods for outbound signing
- Hooks `identity_step_callback` into `step_callback` by default

```python
crew = CloudIdentityCrew.from_env(   # reads CLOUD_ID + CLOUD_PRIVATE_KEY
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    minimum_trust_score=0.5,
)
result = crew.kickoff()

# Sign an outbound request from anywhere in the crew lifecycle:
headers = crew.sign_headers()
```

### Structural primitive #20 — observability callbacks

```python
from crewai import Crew
from citizenofthecloud_crewai import identity_step_callback, identity_task_callback

crew = Crew(
    agents=[...], tasks=[...],
    step_callback=identity_step_callback,   # logs every identity-tool invocation
    task_callback=identity_task_callback,   # flags identity-relevant task completions
)
```

Output is structured-log via `structlog` — pipe it into your existing log aggregator.

---

## Environment variables

| Variable | Description |
|---|---|
| `CLOUD_ID` | Your agent's Cloud ID (e.g., `cc-7f3a9b2e-...`). Read by `CloudIdentityCrew.from_env()`. |
| `CLOUD_PRIVATE_KEY` | Your agent's Ed25519 private key (PEM format). Read by `from_env()`. |
| `COTC_SDK_TOKEN` | Bootstrap SDK token (`cotc_sdk_*`) used by `RegisterAgentTool` and `ReportAgentTool`. Get one at [citizenofthecloud.com/account](https://citizenofthecloud.com/account). |

---

## Links

- [citizenofthecloud.com](https://citizenofthecloud.com)
- [Documentation](https://citizenofthecloud.com/docs)
- [Specification](https://citizenofthecloud.com/spec)
- [Account / SDK tokens](https://citizenofthecloud.com/account)
- Sister framework integrations: [langchain](https://github.com/citizenofthecloud/langchain) · [agent-framework](https://github.com/citizenofthecloud/agent-framework)
- Underlying SDK: [sdk-python](https://github.com/citizenofthecloud/sdk-python)
- [MCP server](https://github.com/citizenofthecloud/mcp-server)

## License

MIT
