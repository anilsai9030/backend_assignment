import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailService:
    """
    Authenticates the user's email account using OAuth2.0 and returns the Gmail service object.
    1) Checks if any tokens.json exists in the directory.
    2) If not, generates a new token and saves it in the directory using credentials.json.
    """

    @staticmethod
    def authenticate_email():
        creds = None
        # Token file stores the user's access and refresh tokens.

        if os.path.exists("./tokens.json"):
            creds = Credentials.from_authorized_user_file("./tokens.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("./config/credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("./tokens.json", "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)
        return service
