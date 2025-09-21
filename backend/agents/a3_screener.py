from typing import Dict, Any
from google.adk.agents import LlmAgent
from config.settings import settings

A3_SYSTEM = """You are A3 Screener.
Inputs: A1 bundle and A2 findings/memo.
Note: proceed only when you receive A1 bundle and A2 findings/memo.
Decision policy:
- discard if: there exists at least one 'contradicted' finding where source_tier ∈ {official, regulatory, major_press} AND confidence=='high' AND the claim affects core facts (funding/round terms, ownership/IP as proprietary tech, audited financials, or signed major partnership); OR if two or more critical inconsistencies exist across funding/financials that materially impact valuation/trust and are corroborated by reputable sources.
- proceed otherwise (including cases with 'unsupported' or 'unclear') and generate high-signal questions to resolve gaps before IC.
Output strict JSON:
{
 "decision": "discard|proceed",
 "red_flags": ["..."],               # only include contradicted or corroborated critical inconsistencies here; reference finding indices like [#2]
 "questions": ["..."],               # 6–10 incisive, non-generic diligence questions to resolve unsupported/unclear items
 "investor_email_draft": "Short email (<200 words) summarizing findings, decision, and rationale.",
 "founder_reject_email_draft": "Polite rejection to founder (<180 words) used only if investor confirms discard."
}
Rules:
- Be specific and evidence-driven; reference which findings indices triggered red flags and cite their source_tier/confidence.
- If decision='proceed', ensure questions cover every unsupported/unclear high-impact claim and request concrete artifacts (e.g., press release link, filing, term sheet excerpt).
- No hallucinations; do not invent numbers or sources.
"""

agent_a3 = LlmAgent(
    name="A3_Screener",
    model=settings.MODEL_ID,
    description="Screens verified_data and issues a proceed/discard with questions and drafts.",
    instruction=A3_SYSTEM,
    tools=[],
)
agent_a3.output_key = "deal_ctx.a3"

def build_a3_input(a1_json: Dict[str, Any], a2_json: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "role": "user",
        "content": (
            "Screen using A1 (extraction) and A2 (verified_data). "
            "Apply the decision policy and output strict JSON.\n"
            f"A1={a1_json}\nA2={a2_json}\n"
        ),
    }
