import datetime
import json
import requests

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# The ID of a sample document.
DOCUMENT_ID = '1ccIkeu2NR6usZEWCok_5qudZBqtR7NWFRqj8RPNOCvA'

TEMPLATE = "./template.json"
INPUT = "./default_input.json"

def get_template():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        with open(TEMPLATE, 'w') as template:
            json.dump(document, template, indent=2)

        print('The title of the document is: {}'.format(document.get('title')))

    except HttpError as err:
        print(err)

def make_new_audit():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        parents_id = ''
        title = "[HEXAudit] DeFiContractAudit_"
        with open(INPUT, "r") as input:
            project_name = json.load(input)["Project-Name"]
            print("project name:", project_name)

            title += project_name + "_v1.0_KR"

            audit_folder_id = "13HWHYSj5RIaN82Sut2lCBVEte8y2V80r"
            folder_metadata = {
                'name' : project_name,
                'parents': [audit_folder_id],
                'mimeType' : 'application/vnd.google-apps.folder'
            }
            folder_response = drive_service.files().create(body=folder_metadata).execute()
            parents_id = folder_response.get('id')

            print("new folder id:", parents_id)


        body = {
            'name': title
        }
        drive_response = drive_service.files().copy(
            fileId=DOCUMENT_ID, body=body).execute()
        audit_docs_id = drive_response.get('id')
        audit_docs = drive_service.files().get(fileId=audit_docs_id,
                                               fields='parents').execute()

        previous_parents_id = ",".join(audit_docs.get('parents'))

        audit_docs_id = drive_service.files().update(fileId=audit_docs_id,
                                                     addParents=parents_id,
                                                     removeParents=previous_parents_id,
                                                     fields='id').execute()

        print("new audit docs id:", audit_docs_id)

    except HttpError as err:
        print(err)

def default_inputs():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        docs_service = build('docs', 'v1', credentials=creds)

        with open(INPUT, 'r') as input:
            inputs = json.load(input)
            date = datetime.datetime.now()

            data = []
            for replacement, value in inputs.items():
                request = {
                    'replaceAllText': {
                        'containsText': {
                            'text': '{{' + replacement + '}}',
                            'matchCase': 'true'
                        },
                        'replaceText': value,
                    }
                }
                data.append(request)

            data.append(
                {
                    'replaceAllText': {
                        'containsText': {
                            'text': '{{date-style1}}',
                            'matchCase': 'true'
                        },
                        'replaceText': date.strftime('%d %b %Y'),
                    }
                }
            )

            data.append(
                {
                    'replaceAllText': {
                        'containsText': {
                            'text': '{{date-style2}}',
                            'matchCase': 'true'
                        },
                        'replaceText': date.strftime('%x'),
                    }
                }
            )

            print(data)
            result = docs_service.documents().batchUpdate(
                documentId=DOCUMENT_ID, body={'requests': data}).execute()


    except HttpError as err:
        print(err)

if __name__ == '__main__':
    #get_template()

    #make_new_audit()
    default_inputs()

