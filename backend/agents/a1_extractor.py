from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from agents.tools.pdf_tools import parse_pdf_tool
from config.settings import settings


A1_SYSTEM = """You are A1 Extractor. 
Tasks:
- Read multi-PDF content and extract a structured bundle:
  founder_profile {name, email, company, linkedin?, location?}
  signals {market, product, team, traction, business_model, competition}
  metrics {revenue, growth_rate, mrr/arr, users, cac, ltv, burn, runway}
  risks {category, detail}[]
- Output ONLY valid JSON with keys: founder_profile, signals, metrics, risks, evidence.
- evidence should cite short quotes from the PDF text when possible.
- Keep strings concise; use null when unknown.
Schema:
{
 "founder_profile": {...},
 "signals": {...},
 "metrics": {...},
 "risks": [{"category": "...","detail": "..."}],
 "evidence": ["..."]
}
"""

# Define A1 as LlmAgent with Gemini and the parse_pdf tool
agent_a1 = LlmAgent(
    name="A1_Extractor",
    model=settings.MODEL_ID,  # e.g., gemini-2.5-flash
    description="Extracts key info from multi-PDF inputs and builds deal context.",
    instruction=A1_SYSTEM,
    tools=[parse_pdf_tool],
)

def build_a1_input(files: List[str]) -> Dict[str, Any]:
    """Helper to form the initial message to A1."""
    return {
        "role": "user",
        "content": f"Parse these PDFs and extract the schema.\nFILES: {files}\n"
    }
