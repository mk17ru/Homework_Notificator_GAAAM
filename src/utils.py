import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = "https://www.googleapis.com/auth/spreadsheets.readonly"


def get_values(id, cells_range):
    if not os.path.exists("token.json"):
        # "Token does not exists"
        return None

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values()
                .get(spreadsheetId=id, range=cells_range)
                .execute()
        )
        values = result.get("values", [])

        if not values:
            # "Values is null"
            return None

        for row in values:
            return str(row)
    except HttpError as err:
        # "Error occured: " + str(err)
        return None
