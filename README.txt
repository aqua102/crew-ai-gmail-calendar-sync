


This is an exercise I did to test out how LLMs can be integrated into apps that call standard API services, such as Google.

When you run : 

python3 main.py

this application will:

1) Check to see if you have any unread Gmails in the past week (this is configurable).
2) If you do, grab the emails and send them to Chat GPT Mini, (configurable) and prompt the LLM to look for invitations in the emails that contain certain keywords.
3) If such invitations exist, the LLM will return json containing the invitation. The JSON is formatted with the Google Calendar API in mind.
4) Use the returned invitation JSON (if its returned) to post to the Google Calendar API, 
   thereby creating calendar invite entries. The resulting calendar invites should have a tentative status.

Dependencies: 

1) A Gmail account. 

2) Install the requirements.txt file via: pip install -r /path/to/this/application/requirements.txt
   There may be some other dependencies you find that you'll need to install. If so: apologies in advance!

3) Google Cloud console oauth permissions that will allow this application to access your Gmail and    
   Google Calendar APIs.
   
   You can google "steps to get oauth permissions on google cloud" for clear instructions on how to do this.
   
   You'll use the resulting credentials in json form to populate the included client_secret.json and credentials.json files. 
   
   Note that gmail_token.json and token.json files will be automatically generated in your local app codebase when you first complete this permissioning process.

4) A Chat GPT Mini API account. 

