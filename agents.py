from crewai import Agent
from textwrap import dedent
from langchain_openai import ChatOpenAI

class GmailCalendarSyncAgents:
    def __init__(self):
        self.OpenAIGPT4 = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

    def email_check(self):
        return Agent(
            role="Email Checker",
            goal="Determine if any of the list of emails you receive contain an invitation.",
            backstory="An expert in analyzing email to see if contains an invitation that might be relevant to the app user.",
            tools=[],
            verbose=True,
        )
