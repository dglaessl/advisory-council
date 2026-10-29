#!/usr/bin/env python3
"""Hospitality Crew (seat hospitality-crew): Casa La Fonte, the Tuscan farmhouse.

market comps analyst -> pricing analyst -> listing editor -> agency-performance reviewer

ANALYSIS ONLY: never publishes listings, changes prices, or contacts the agency,
guests or anyone else. Every recommendation is a proposal for Daniel.
No guest personal data goes into this crew.

Usage: python crews/hospitality.py ENVELOPE.json [--out DIR] [--input-dir DIR] [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CrewResult, council_rules, run  # noqa: E402
from pydantic import BaseModel  # noqa: E402

SEAT = "hospitality-crew"


class HospitalityProposal(BaseModel):
    area: Literal["pricing", "listing", "agency", "other"]
    proposal: str
    rationale: str
    expected_effect: str
    how_to_measure: str
    needs_daniel_approval: bool = True


class HospitalityResult(CrewResult):
    proposals: list[HospitalityProposal]


def build_crew(env, brief, llm, tools):
    from crewai import Agent, Crew, Process, Task

    rules = council_rules() + (
        "\n- This crew is ANALYSIS ONLY: you never publish or edit the listing, never change "
        "prices or availability, and never contact the agency, guests or platforms. You write "
        "proposals; Daniel and Eva decide and act.\n- Never include guest names, messages or "
        "other personal data.")

    def agent(role, goal, backstory, use_tools=False):
        return Agent(role=role, goal=goal, backstory=f"{backstory}\n\n{rules}", llm=llm,
                     tools=tools if use_tools else [], allow_delegation=False, verbose=False,
                     max_iter=6)

    comps = agent("Market comps analyst",
                  "Build a comparable set for a Tuscan farmhouse rental and summarize rates, "
                  "occupancy signals and seasonality with sources and dates.",
                  "You analyze short-let markets in rural Tuscany.", use_tools=True)
    pricing = agent("Pricing analyst",
                    "Propose seasonal price bands and minimum-stay ideas as hypotheses to test.",
                    "You price vacation rentals from comps and seasonality.")
    editor = agent("Listing editor",
                   "Propose concrete listing improvements (title, photos order, description, "
                   "amenities) as draft text for Daniel to review.",
                   "You edit vacation-rental listings for clarity and conversion.")
    reviewer = agent("Agency-performance reviewer",
                     "Assess the property management agency's performance from the data provided, "
                     "list questions for Daniel to raise with them, and write the final structured answer.",
                     "You review property management agencies against market benchmarks, fairly.")

    t1 = Task(description=f"{brief}\n\nBuild the comp set and market read.",
              expected_output="Comp set and market read with sources and dates.", agent=comps)
    t2 = Task(description="Propose seasonal price bands and stay rules as testable hypotheses. "
                          "These are proposals only; do not state that any price was changed.",
              expected_output="Price-band hypotheses with rationale.", agent=pricing, context=[t1])
    t3 = Task(description="Propose listing edits as draft text for Daniel to review.",
              expected_output="Listing edit proposals.", agent=editor, context=[t1, t2])
    t4 = Task(description=(
        "Write the final answer for the Chair. Review agency performance against the comps, "
        "then list every pricing, listing and agency proposal (each needs Daniel's approval), "
        "findings with sources, assumptions, confidence, open questions, actions only Daniel or "
        "Eva may take, and an employment-conflict check (Casa La Fonte is privately owned; check "
        "it anyway, e.g. use of employer time or devices). Memo at most 300 words."),
        expected_output="JSON matching the HospitalityResult schema.",
        agent=reviewer, context=[t1, t2, t3], output_pydantic=HospitalityResult)
    return Crew(agents=[comps, pricing, editor, reviewer], tasks=[t1, t2, t3, t4],
                process=Process.sequential, verbose=False)


def postprocess(r: HospitalityResult) -> HospitalityResult:
    # Every proposal is Daniel's call, whatever the model said.
    for p in r.proposals:
        p.needs_daniel_approval = True
    note = "No proposal has been applied; publishing, price changes and agency contact are Daniel's."
    if note not in r.actions_requiring_daniel:
        r.actions_requiring_daniel.append(note)
    return r


if __name__ == "__main__":
    sys.exit(run(SEAT, HospitalityResult, build_crew, postprocess))
