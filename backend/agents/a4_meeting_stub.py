from google.adk.agents import Agent

agent_a4 = Agent(
    name="A4_MeetingStub",
    model="none",
    description="Stub meeting agent that returns canned notes for now.",
    instruction="Return a JSON object with 'notes' summarizing QnA answers (stubbed).",
    tools=[],
)
