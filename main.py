import os
import re
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import OpenAI
from decouple import config
from textwrap import dedent
from agents import GmailCalendarSyncAgents
from tasks import GmailCalendarSyncTasks
from get_emails import GetGmails
import json
from post_gmail_event import post_event

# see: https://python.langchain.com/docs/versions/v0_3/ for upgrading langchain
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["OPENAI_ORGANIZATION"] = config("OPENAI_ORGANIZATION_ID")


class GmailCalendarSyncCrew:

    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = GmailCalendarSyncAgents()
        # We don't want to bombard your google calendar with just any invitation. Create a comma delimited whitelist of subjects to look for as a rough filter.
        # If the below string isn't found in the body of the email, then it's not a postable event.
        email_content_whitelist = ['A','COMMA','DELIMITED','LIST','OF','PERSONALLY', 'RELEVANT','KEYWORDS']
        tasks = GmailCalendarSyncTasks(email_content_whitelist)
        number_of_emails = 6
        mails = GetGmails().get_mail_list(number_of_emails)

        if mails and mails is not None:

            scan_email_agent = agents.email_check()
            email_recipient = mails[0]["to"]
            match = re.search(
                r"<(.*?)>", email_recipient
            )  # strip angle brackets from email recip
            if match:
                value = match.group(1)
                email_recipient = value
            email_bodies = []
            for mail in mails:

                email_bodies.append(
                    mail["body"]
                )

            scan_email_task = tasks.scan_email_task(
                scan_email_agent, email_bodies, email_recipient
            )

            crew = Crew(
                agents=[scan_email_agent],
                tasks=[scan_email_task],
                verbose=True,
            )

            result = crew.kickoff()
            return result
        else:
            print("No unread emails were found to send to model.")
    
    def get_valid_json(self, event_string):
        try:
            event_obj_json = json.loads(event_string)
        except ValueError as e:
            return False
        return event_obj_json
        
        
    def insert_google_calendar_event(self, event_json):
          
        for event in event_json:
                print("Event to POST is: ")
                print(event)
                post_event(event)
        else:
            return False


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":

    custom_crew = GmailCalendarSyncCrew()
    results = custom_crew.run()
    
    if results and results.raw is not None:
        #The LLM seems determined to return json wrapped in back ticks with the label 'json'. 
        # Though we'ved asked the LLM not to do this, strip them just in case, 
        # because python doesn't like them when trying to load them as json.
        possible_events = results.raw.replace("```", "")
        event_obj_json = custom_crew.get_valid_json(possible_events)
        if event_obj_json and event_obj_json is not None:    
            custom_crew.insert_google_calendar_event(event_obj_json)
        else:
            print("No valid events were found to post.")    
    else:
        print("No eligible emails found")
