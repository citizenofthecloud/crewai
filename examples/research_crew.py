"""
Example: CrewAI research crew with Cloud Identity verification.

This crew verifies external agents before accepting work from them,
checks trust scores before delegating to other agents, and signs
all outbound requests.

Requirements:
    pip install citizenofthecloud citizenofthecloud-crewai crewai

Environment:
    OPENAI_API_KEY=sk-...
    CLOUD_ID=cc-...
    CLOUD_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
"""

from crewai import Agent, Task
from citizenofthecloud_crewai import CloudIdentityCrew, cloud_identity_tools


def main():
    # ── Agents with identity tools ──

    researcher = Agent(
        role="Senior Research Analyst",
        goal="Gather comprehensive information from verified sources only",
        backstory=(
            "You are a senior research analyst with access to the Citizen "
            "of the Cloud identity protocol. Before accepting data from any "
            "external agent, you ALWAYS verify their identity and check "
            "their trust score. You refuse to work with agents below a "
            "0.5 trust score or those who haven't signed the covenant."
        ),
        tools=cloud_identity_tools(),
        verbose=True,
        allow_delegation=False,
    )

    analyst = Agent(
        role="Trust-Aware Data Analyst",
        goal="Analyze data with full awareness of source trustworthiness",
        backstory=(
            "You are a data analyst who weighs the reliability of data "
            "based on the trust score of the agent that provided it. "
            "Higher trust scores mean more reliable data. You always "
            "note the trust level of your sources in your analysis."
        ),
        tools=cloud_identity_tools(),
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role="Report Writer",
        goal="Produce clear, well-sourced reports with trust attributions",
        backstory=(
            "You write reports that include trust attributions for every "
            "source. Each claim is tagged with the trust score of the "
            "agent that provided the underlying data."
        ),
        verbose=True,
        allow_delegation=False,
    )

    # ── Tasks ──

    verify_sources = Task(
        description=(
            "Look up the following agents in the Cloud Identity registry "
            "and check their trust scores. Report which ones are safe "
            "to accept data from (trust score >= 0.6, covenant signed):\n"
            "- cc-7f3a9b2e-4d1c-8e7f-a3b2-9c1d5e8f4a6b\n"
            "- cc-82d8afc8-d1ef-4ec7-b3d0-6e613ea683ab\n"
        ),
        expected_output=(
            "A list of each agent with their trust score, covenant status, "
            "and whether they are approved as data sources."
        ),
        agent=researcher,
    )

    analyze_data = Task(
        description=(
            "Using the verified source list from the previous task, "
            "analyze the research topic: '{topic}'. Only reference data "
            "from agents that passed the trust check. For each finding, "
            "note which agent provided it and their trust score."
        ),
        expected_output=(
            "Analysis findings with trust-attributed sources."
        ),
        agent=analyst,
        context=[verify_sources],
    )

    write_report = Task(
        description=(
            "Write a final report on '{topic}' based on the trust-verified "
            "analysis. Include a 'Source Trust' section at the end that "
            "lists each contributing agent and their trust score."
        ),
        expected_output=(
            "A complete report with trust attributions for all sources."
        ),
        agent=writer,
        context=[analyze_data],
    )

    # ── Crew with Cloud Identity ──

    crew = CloudIdentityCrew.from_env(
        agents=[researcher, analyst, writer],
        tasks=[verify_sources, analyze_data, write_report],
        minimum_trust_score=0.5,
        verbose=True,
    )

    # ── Execute ──

    result = crew.kickoff(inputs={
        "topic": "Current trends in AI agent orchestration frameworks"
    })

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result.raw)


if __name__ == "__main__":
    main()
