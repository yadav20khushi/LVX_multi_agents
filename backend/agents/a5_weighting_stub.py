from google.adk.agents import Agent

agent_a5 = Agent(
    name="A5_WeightingStub",
    model="none",
    description="Stub weighting agent that returns a canned weighted recommendation.",
    instruction="Return JSON: { 'weighted_reco': '[stubbed] proceed', 'score': 0.78 }",
    tools=[],
)
