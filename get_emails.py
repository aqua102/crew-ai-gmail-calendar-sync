from simplegmail import Gmail
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class GetGmails:

    def receive_recent_emails(self, max_results=10):

        gmail = Gmail()

        today = datetime.today()
        one_week_ago = today - timedelta(weeks=1)
        tomorrow = today + timedelta(days=1)
        today = today.strftime("%Y/%m/%d")
        one_week_ago = one_week_ago.strftime("%Y/%m/%d")
        tomorrow = tomorrow.strftime("%Y/%m/%d")

        try:

            # Fetch the messages with the specified query
            # https://developers.google.com/gmail/api/guides/filtering
            response = (
                gmail.service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=["INBOX"],
                    maxResults=max_results,
                    q="is:unread in:inbox after:" + one_week_ago + " before:" + tomorrow,
                )
                .execute()
            )

            messages = response.get("messages", [])
            email_data = []

            for msg in messages:

                message = (
                    gmail.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"])
                    .execute()
                )

                email_info = {
                    "date": next(
                        header["value"]
                        for header in message["payload"]["headers"]
                        if header["name"] == "Date"
                    ),
                    "to": next(
                        header["value"]
                        for header in message["payload"]["headers"]
                        if header["name"] == "To"
                    ),
                    "subject": next(
                        header["value"]
                        for header in message["payload"]["headers"]
                        if header["name"] == "Subject"
                    ),
                    "sender": next(
                        header["value"]
                        for header in message["payload"]["headers"]
                        if header["name"] == "From"
                    ),
                    "body": self.get_message_body(message["payload"]),
                }
                email_data.append(email_info)

            # Mark the email as read
            gmail.service.users().messages().modify(userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"]}).execute()
            
            return email_data

        except HttpError as error:
            print(f"An error occurred: {error}")
            print(f"Error details: {error.content}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

    def get_message_body(self, payload):
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body += base64.urlsafe_b64decode(
                        part["body"].get("data", "")
                    ).decode("utf-8")
                elif part["mimeType"] == "text/html":
                    body += base64.urlsafe_b64decode(
                        part["body"].get("data", "")
                    ).decode("utf-8")
        else:
            body += base64.urlsafe_b64decode(payload["body"].get("data", "")).decode(
                "utf-8"
            )

        return body


    def get_mail_list(self, number_of_most_recent_emails):

        emails = self.receive_recent_emails(number_of_most_recent_emails)

        email_list = []

        if emails is not None:

            for email in emails:
                email_item = {}
                email_item["to"] = email["to"]
                email_item["from"] = email["sender"]
                email_item["subject"] = email["subject"]
                email_item["body"] = "Sent: " + email["date"] + " "
                cleantext = BeautifulSoup(email["body"], "html.parser").text.strip()
                cleanertext = (
                    cleantext.replace("\n", "").replace("\r", "").replace("<br/>", "")
                )
                email_item["body"] += cleanertext
                email_list.append(email_item)
        else:
            return False

        return email_list
