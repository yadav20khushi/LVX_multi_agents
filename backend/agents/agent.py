from google.adk.agents import SequentialAgent
from agents.a1_extractor import agent_a1
from agents.a2_verifier import agent_a2
from agents.a3_screener import agent_a3

agent_a1.name = "A1_Extractor"
agent_a2.name = "A2_Verifier"
agent_a3.name = "A3_Screener"

agent_a1.output_key = "deal_ctx.a1"
agent_a2.output_key = "deal_ctx.a2"
agent_a3.output_key = "deal_ctx.a3"

LVX_Orchestrator = SequentialAgent(
    name="LVX_Orchestrator",
    description="Runs A1 → A2 → A3 sequentially and stores outputs in state.deal_ctx.*",
    sub_agents=[agent_a1, agent_a2, agent_a3],
)

root_agent = LVX_Orchestrator
