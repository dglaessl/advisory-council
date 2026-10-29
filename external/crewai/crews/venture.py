#!/usr/bin/env python3
"""Venture Crew (seat venture-crew): the agent-driven side business.

market researcher -> customer analyst -> positioning strategist -> pricing analyst

Usage: python crews/venture.py ENVELOPE.json [--out DIR] [--input-dir DIR] [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CrewResult, EmploymentConflictCheck, council_rules, run, worst_status  # noqa: E402
from pydantic import BaseModel  # noqa: E402

SEAT = "venture-crew"


class VentureOption(BaseModel):
    name: str
    target_customer: str
    problem_and_evidence: str
    positioning: str
    price_hypothesis: str
    cheapest_first_test: str
    employment_conflict_check: EmploymentConflictCheck


class VentureResult(CrewResult):
    options: list[VentureOption]


def build_crew(env, brief, llm, tools):
    from crewai import Agent, Crew, Process, Task

    rules = council_rules()
    focus_note = ("The side business focus is NOT settled. Longevity/health was one first "
                  "idea; treat it as one option among others unless the task says otherwise.")

    def agent(role, goal, backstory, use_tools=False):
        return Agent(role=role, goal=goal, backstory=f"{backstory}\n\n{rules}", llm=llm,
                     tools=tools if use_tools else [], allow_delegation=False, verbose=False,
                     max_iter=6)

    researcher = agent(
        "Market researcher",
        "Size and map the markets relevant to the task, with sourced, dated facts.",
        "You map markets for small, agent-driven businesses run by one person on personal time.",
        use_tools=True)
    customer = agent(
        "Customer analyst",
        "Identify who would pay, for what job, and how to reach them cheaply.",
        "You turn market maps into specific customer segments and jobs-to-be-done.")
    positioning = agent(
        "Positioning strategist",
        "Find a defensible position that fits Daniel's skills and avoids his employer's field.",
        "You write sharp positioning for solo founders with domain expertise in architecture, "
        "product development, research and longevity.")
    pricing = agent(
        "Pricing analyst",
        "Propose price hypotheses and the cheapest test for each option, then run the "
        "employment-conflict check and write the final structured answer.",
        "You design pricing experiments and you are careful about conflicts of interest.")

    t1 = Task(description=f"{brief}\n\n{focus_note}\n\nResearch the markets this task concerns. "
                          "List facts with source and date; flag what you could not verify.",
              expected_output="Market map: segments, size signals, competitors, trends, each with source/date.",
              agent=researcher)
    t2 = Task(description="From the market map, identify 3-5 customer segments, their job-to-be-done, "
                          "willingness to pay signals and reach channels.",
              expected_output="Customer segments with jobs, pains, reach and evidence.",
              agent=customer, context=[t1])
    t3 = Task(description="Propose 2-4 business options with positioning. For each, say how it uses "
                          "Daniel's own skills and why it stays outside his employer's field.",
              expected_output="Options with positioning statements and fit rationale.",
              agent=positioning, context=[t1, t2])
    t4 = Task(description=(
        "Write the final answer for the Chair. For each option add a price hypothesis, the "
        "cheapest first test (no spending or outreach without Daniel's approval) and an "
        "employment-conflict check. Then give an overall employment-conflict check (the worst "
        "of the options), findings with sources, assumptions, confidence, open questions and "
        "the actions only Daniel may take. Memo at most 300 words."),
        expected_output="JSON matching the VentureResult schema.",
        agent=pricing, context=[t1, t2, t3], output_pydantic=VentureResult)
    return Crew(agents=[researcher, customer, positioning, pricing], tasks=[t1, t2, t3, t4],
                process=Process.sequential, verbose=False)


def postprocess(r: VentureResult) -> VentureResult:
    statuses = [o.employment_conflict_check.status for o in r.options]
    r.employment_conflict_check.status = worst_status(r.employment_conflict_check.status, *statuses)
    return r


if __name__ == "__main__":
    sys.exit(run(SEAT, VentureResult, build_crew, postprocess))
