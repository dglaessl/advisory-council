#!/usr/bin/env python3
"""Career & Offers Crew (seat career-crew): the long-term AI-expert horizon.

AI-market scout -> domain-fit analyst -> offer designer -> pricing analyst

Every offer carries its own employment-conflict check (outside-work, IP,
non-compete) before it is proposed.

Usage: python crews/career.py ENVELOPE.json [--out DIR] [--input-dir DIR] [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CrewResult, EmploymentConflictCheck, council_rules, run, worst_status  # noqa: E402
from pydantic import BaseModel  # noqa: E402

SEAT = "career-crew"


class Offer(BaseModel):
    name: str
    format: Literal["advisory", "fractional", "tool", "course", "writing", "talk", "other"]
    buyer: str
    domain_fit: str
    price_hypothesis: str
    proof_needed: str
    cheapest_test: str
    employment_conflict_check: EmploymentConflictCheck


class CareerResult(CrewResult):
    offers: list[Offer]


def build_crew(env, brief, llm, tools):
    from crewai import Agent, Crew, Process, Task

    rules = council_rules()
    domains = ("product development, real estate development, architecture and design, "
               "longevity, and research")

    def agent(role, goal, backstory, use_tools=False):
        return Agent(role=role, goal=goal, backstory=f"{backstory}\n\n{rules}", llm=llm,
                     tools=tools if use_tools else [], allow_delegation=False, verbose=False,
                     max_iter=6)

    scout = agent("AI-market scout",
                  "Map where demand and pay exist for AI expertise, with sources and dates.",
                  "You track the market for AI skills: roles, contracts, tools, courses.",
                  use_tools=True)
    fit = agent("Domain-fit analyst",
                f"Match that demand to Daniel's domains: {domains}.",
                "You find where domain expertise plus AI skill commands a premium.")
    designer = agent("Offer designer",
                     "Turn the best fits into concrete, testable offers.",
                     "You design offers (advisory, fractional, tools, courses, writing) for experts.")
    pricing = agent("Pricing analyst",
                    "Price each offer, define its cheapest test, run the employment-conflict "
                    "check per offer and write the final structured answer.",
                    "You price expert services and you are careful about conflicts of interest.")

    t1 = Task(description=f"{brief}\n\nMap AI-skill demand and pay.",
              expected_output="Demand map with sources and dates.", agent=scout)
    t2 = Task(description=f"Score fit against Daniel's domains ({domains}).",
              expected_output="Ranked domain-fit list with reasons.", agent=fit, context=[t1])
    t3 = Task(description="Design 3-5 offers from the top fits. Say what proof each needs.",
              expected_output="Offer drafts.", agent=designer, context=[t1, t2])
    t4 = Task(description=(
        "Write the final answer for the Chair. For each offer: price hypothesis, cheapest test "
        "(no outreach or spending without Daniel's approval), and an employment-conflict check "
        "(outside the employer's field? any employer time, devices, info or contacts? IP "
        "assignment? non-compete / non-solicit?). Drop or flag any offer that conflicts. Add an "
        "overall check (the worst of the offers), findings with sources, assumptions, confidence, "
        "open questions and actions only Daniel may take. Memo at most 300 words."),
        expected_output="JSON matching the CareerResult schema.",
        agent=pricing, context=[t1, t2, t3], output_pydantic=CareerResult)
    return Crew(agents=[scout, fit, designer, pricing], tasks=[t1, t2, t3, t4],
                process=Process.sequential, verbose=False)


def postprocess(r: CareerResult) -> CareerResult:
    statuses = [o.employment_conflict_check.status for o in r.offers]
    r.employment_conflict_check.status = worst_status(r.employment_conflict_check.status, *statuses)
    return r


if __name__ == "__main__":
    sys.exit(run(SEAT, CareerResult, build_crew, postprocess))
