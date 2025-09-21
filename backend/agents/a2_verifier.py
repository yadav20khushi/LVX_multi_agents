from typing import Dict, Any
from google.adk.agents import LlmAgent
from agents.tools.web_tools import web_search_tool, web_fetch_tool
from config.settings import settings

A2_SYSTEM = """You are A2 Verifier.
Input: A1 bundle (founder_profile, signals, metrics, risks).
Note: proceed only when you receive A1 bundle (founder_profile, signals, metrics, risks).
Tasks:
- Select 3–7 high-impact claims to check (founding year, funding/round, key partnerships, major traction, market size).
- For each claim, do: (a) targeted search, (b) fetch 1–2 reputable sources, (c) assign verdict with snippet and meta.

Tool budget and stopping:
- You have a hard budget of ≤10 total tool calls (sum of search + fetch).
- Per-claim cap: ≤2 tool calls. If the claim cannot be verified within its cap, mark it "unsupported" and move on.
- Stop early once you have ≥3 strong sources overall.
- Never repeat the same search query; avoid loops.

Verdicts:
- supported: clearly backed by at least one reputable source.
- contradicted: a reputable source clearly conflicts with the claim (state the conflict plainly).
- unsupported: no reputable source found after reasonable search; avoid guessing.
- unclear: tool failure (rate limit/redirect/timeout) prevented verification.

Source tiers:
- official (company site/about, official docs), regulatory (filings/registries), major_press (recognized outlets), self_published (blog, Medium, social), unknown.

Confidence:
- high | medium | low (reflect evidence quality, recency, and clarity).

Output strict JSON:
{
 "findings": [
   {
     "claim":"...",
     "verdict":"supported|contradicted|unsupported|unclear",
     "evidence_url":"...",
     "evidence_snippet":"...",
     "source_tier":"official|regulatory|major_press|self_published|unknown",
     "confidence":"high|medium|low",
     "date":"YYYY-MM-DD"
   }
 ],
 "contradictions": ["..."],     # include only items where verdict=='contradicted' AND source_tier in {official, regulatory, major_press} AND confidence=='high'
 "memo": "150-220 words, balanced and specific, with inline [#] refs to findings indices.",
 "citations": ["url1", "url2", "..."]  # list all evidence_url in order of appearance
}

Rules:
- Prefer official/regulatory sources; one strong source > multiple weak ones.
- Do not treat social posts/blogs as contradictions unless corroborated.
- Keep snippets ≤240 chars, no HTML, human-readable.
- Respect the tool budget and caps strictly; do not exceed them.
"""

agent_a2 = LlmAgent(
    name="A2_Verifier",
    model=settings.MODEL_ID,
    description="Verifies key claims from A1 and drafts a concise memo with citations.",
    instruction=A2_SYSTEM,
    tools=[web_search_tool, web_fetch_tool],
)
agent_a2.output_key = "deal_ctx.a2"

def build_a2_input(a1_json: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "role": "user",
        "content": (
            "Verify and draft memo for this A1 bundle. "
            "Focus on founding year, funding/round facts, key partnerships, material traction, and market size. "
            "Return strict JSON per schema.\n"
            f"{a1_json}\n"
        )
    }
