import config
import os.path
import json
import datetime
from tzlocal import get_localzone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def auth_cal():
    creds = None
    if os.path.exists(config.TOKENS):
        try:
            creds = Credentials.from_authorized_user_file(config.TOKENS, config.SCOPES)
        except Exception as e:
            print(f"Error loading token file ({config.TOKENS}): {e}.")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Reloading expired Google API token!")
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print("Please re-authenticate.")
                creds = None

        if not creds:
            try:
                print("Restarting Google API authentication")
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS, config.SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print(f"Credentials file '{config.CREDENTIALS}' not found.")
                return None
            except Exception as e:
                print(f"Error during authentication flow: {e}")
                return None

        if creds:
            try:
                with open(config.TOKENS, 'w') as token:
                    token.write(creds.to_json())
                print(f"Credentials saved to {config.TOKENS}")
            except Exception as e:
                print(f"Error saving token file: {e}")

    if not creds:
        print("Valid Credentials not found!")
        return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        print("Google Calendar API authentication successful!")
        return service
    except HttpError as error:
        print(f'Error occurred during Google Calendar service build: {error}')
        return None
    except Exception as e:
        print(f'Error occurred during authentication: {e}')
        return None

def rfc3339(dt_obj):
    if dt_obj is None:
        return None

    if dt_obj.tzinfo is None or dt_obj.tzinfo.utcoffset(dt_obj) is None:
        try:
            local_tz = get_localzone()
            if local_tz:
                dt_obj = dt_obj.replace(tzinfo=local_tz)
            else:
                print(f"Failed to get local timezone. Timezone info will be missing.")
        except Exception as e:
            print(f"Failed to get local timezone ({e}). Timezone info will be missing.")

    return dt_obj.isoformat()

def createcalendarevent(service, event_details):
    if not service:
        print("Calendar Service not working or available!")
        return False
    if not all(k in event_details for k in ['title', 'start_dt', 'end_dt']):
        print("Error: Missing required event details (title, start_dt, end_dt).")
        return False
    if not event_details['title'] or not event_details['start_dt'] or not event_details['end_dt']:
        print("Required event details (title, start_dt, end_dt) cannot be empty.")
        return False

    starttime_rfc = rfc3339(event_details['start_dt'])
    endtime_rfc = rfc3339(event_details['end_dt'])

    if not starttime_rfc or not endtime_rfc:
        print("Could not format start or end time for the API. Check warnings above.")
        return False
    if not ('+' in starttime_rfc or '-' in starttime_rfc or 'Z' in starttime_rfc):
        print(f"Error: Formatted start time '{starttime_rfc}' still lacks timezone info.")
        return False
    if not ('+' in endtime_rfc or '-' in endtime_rfc or 'Z' in endtime_rfc):
        print(f"Error: Formatted end time '{endtime_rfc}' still lacks timezone info.")
        return False

    event = {
        'summary': event_details['title'],
        'start': {
            'dateTime': starttime_rfc,
        },
        'end': {
            'dateTime': endtime_rfc,
        },
    }

    try:
        print(f"Creating event: {event['summary']} from {starttime_rfc} to {endtime_rfc}")
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created successfully: {created_event.get('htmlLink')}")
        return True
    except HttpError as error:
        print(f'An error occurred creating the calendar event: {error}')
        try:
            errorval = json.loads(error.content)
            print("Error details:", errorval.get('error', {}).get('message'))
        except:
            print("Could not parse specific error details from response.")
        return False
    except Exception as e:
        print(f'An unexpected error occurred during event creation: {e}')
        return False
