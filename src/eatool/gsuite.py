import csv
import io
import json
from functools import cached_property

import keyring
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GSuite:
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    OAUTH_CREDS = {
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "client_id": "675767516221-fphq122iepql9vg21ihl7nan08j9lem6.apps.googleusercontent.com",
        "client_secret": None,
        "project_id": "eatool-385421",
        "redirect_uris": ["http://localhost"],
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    @cached_property
    def calsvc(self):
        creds = self.get_credentials()
        return build("calendar", "v3", credentials=creds)

    @cached_property
    def sheetsvc(self):
        creds = self.get_credentials()
        return build("sheets", "v4", credentials=creds)

    def clear_credentials(self, client_secret=False):
        try:
            keyring.delete_password("eatool", "gsuite")
        except keyring.errors.PasswordDeleteError:
            pass

        if client_secret:
            try:
                keyring.delete_password("eatool", "gsuite-client-secret")
            except keyring.errors.PasswordDeleteError:
                pass

    def get_credentials(self):
        creds = None

        tokendata = keyring.get_password("eatool", "gsuite")
        if tokendata:
            creds = Credentials.from_authorized_user_info(info=json.loads(tokendata))

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                oauth_secret = keyring.get_password("eatool", "gsuite-client-secret")
                if not oauth_secret:
                    oauth_secret = input(
                        "Please enter OAuth Client Secret (check with Philipp): "
                    )
                    keyring.set_password("eatool", "gsuite-client-secret", oauth_secret)

                oauth_creds = GSuite.OAUTH_CREDS.copy()
                oauth_creds["client_secret"] = oauth_secret

                flow = InstalledAppFlow.from_client_config(
                    {"installed": oauth_creds}, scopes=GSuite.SCOPES
                )
                creds = flow.run_local_server(port=0)

            keyring.set_password("eatool", "gsuite", creds.to_json())

        return creds

    def set_event_attendees(self, calendar_id, event_id, attendees, notify=True):
        event = (
            self.calsvc.events().get(calendarId=calendar_id, eventId=event_id).execute()
        )
        event["attendees"] = [{"email": email} for email in attendees]
        sendUpdates = "all" if notify else "none"
        return (
            self.calsvc.events()
            .update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates=sendUpdates,
            )
            .execute()
        )

    def list_events(self, calendar_id, time_min=None, time_max=None, query=None):
        events_result = (
            self.calsvc.events()
            .list(
                calendarId=calendar_id,
                q=query,
                timeMin=time_min.astimezone().isoformat(),
                timeMax=time_max.astimezone().isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    def sheetcsv(self, file_id, sheetName=None, cellRange=None):
        sheet_metadata = (
            self.sheetsvc.spreadsheets().get(spreadsheetId=file_id).execute()
        )

        if sheetName and sheetName.isdigit():
            # Assume this is a gid
            sheets = sheet_metadata.get("sheets", [])
            sheetName = int(sheetName)

            for sheet in sheets:
                if sheet["properties"]["sheetId"] == sheetName:
                    sheetName = sheet["properties"]["title"]
            if not sheetName:
                raise Exception("Could not find sheet " + sheetName)

        elif not sheetName:
            try:
                sheetName = sheet_metadata["sheets"][0]["properties"]["title"]
            except KeyError:
                sheetName = "Sheet1"

        fullRange = f"{sheetName}!{cellRange}" if cellRange else sheetName
        sheet = (
            self.sheetsvc.spreadsheets()
            .values()
            .get(spreadsheetId=file_id, range=fullRange)
            .execute()
        )
        rows = filter(None, sheet.get("values", []))

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output.getvalue()

    def calendar_by_name(self, name):
        calendar_list = self.calsvc.calendarList().list().execute()

        for entry in calendar_list["items"]:
            if entry["summary"] == name:
                return entry["id"]

        return None
