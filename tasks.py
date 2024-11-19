from crewai import Task
from textwrap import dedent
import datetime


# This is an example of how to define custom tasks.
# You can define as many tasks as you want.
# You can also define custom agents in agents.py
class GmailCalendarSyncTasks:

    def __init__(self, keyword_whitelist):
        self.keyword_whitelist = keyword_whitelist

    def scan_email_task(self, agent, email_list, email_recipient):

        prompt = self.build_prompt(email_recipient)
        #print("email list we're sending to the model is: ")
        #print(email_list)

        return Task(
            description=dedent(
                f"""
                As an email checker, please determine if any email in the submitted email array contains an invitation.
                {email_list}
            """
            ),
            agent=agent,
            expected_output=prompt,
        )

    def build_prompt(self, email_recipient):

        current_year = datetime.datetime.now().year

        prompt = "\n Check each email body in the submitted array to see if it looks like an invitation to some type of event."
        prompt += "\n If any of the given email bodies in the array are perceived as an invitation, also make sure the email body includes at least one of the following whitelist words:"
        prompt += "\n " + ",".join(self.keyword_whitelist)
        prompt += "\n If the given email body is perceived to be an invitation and does in fact include one of these whitelist words, consider the email invitation to be valid."
        prompt += "\n If the email is perceived to be an invitation, consider the possibility that the email might have the whitelist words wrapped in html markup. If one or more are found this way, then consider the invitation valid."
        prompt += "\n If the email is perceived to be an invitation but does not include any of these whitelist words, consider invitation invalid. Also indicate invitations were found, but were blocked from entering calendar."
        prompt += "\n If the email is a valid invitation, also make sure the start and end timezone values align with the given event location."
        prompt += "\n If the email is a valid invitation, translate it into the following json structure, populating each key with the appropriate, corresponding value where possible."
        prompt += "\n"
        # Since we're interpolating a variable in the next string output, note that we need to include escape curly braces.
        prompt += f"""{{
                        "summary": "",
    "location": "",
    "description": "",
    "start": {{
        "dateTime": "",
        "timeZone": ""
    }},
    "end": {{
        "dateTime": "",
        "timeZone": ""
    }},
    "recurrence": [],
    "attendees": [
        {{
            "email": "{email_recipient}",
            "responseStatus": "needsAction"
        }}
    ],
    "reminders": {{
        "useDefault": "",
        "overrides": []
                   }}
            }}
        """

        prompt += (
            "\n If the year is not specified, assume it is the year "
            + str(current_year)
            + "."
        )

        prompt += "\n The value for attendees.email will always be the email address of the recipient."
        prompt += "\n Make sure start and end times show GMT time zone offsets, using standard RFC339 format."
        prompt += "\n If such a valid json invitation object is created, then push this created json object into a json array, ie, []"
        prompt += "\n Return an array of valid json invitation objects (if they exist) in the previously mentioned format. But wrap the objects in [] brackets."
        prompt += "\n Very important: If returning json, do not wrap the json array brackets in back ticks and do not have the label 'json' mentioned outside the brackets"

        return prompt
