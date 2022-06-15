from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import json


class DocsManager:
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    DOCUMENT_ID = '1ccIkeu2NR6usZEWCok_5qudZBqtR7NWFRqj8RPNOCvA'
    AUDIT_FOLDER_ID = "13HWHYSj5RIaN82Sut2lCBVEte8y2V80r"

    TEMPLATE = "./template.json"

    def __init__(self, data):
        self.data = data
        self.creds = None
        self._oauth()

        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)

    def _oauth(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def get_docs(self, documentId):
        if self.creds is None:
            self._oauth()
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)

        try:
            # Retrieve the documents contents from the Docs service.
            document = self.docs_service.documents().get(documentId=documentId).execute()

            with open(self.TEMPLATE, 'w') as template:
                json.dump(document, template, indent=2)

            print('The title of the document is: {}'.format(document.get('title')))

        except HttpError as err:
            print(err)

    def search_folder(self, name):
        if self.creds is None:
            self._oauth()
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)

        try:
            page_token = None

            while True:
                response = self.drive_service.files().list(q="mimeType=application/vnd.google-apps.folder",
                                                           spaces='drive',
                                                           fields='nextPageToken, files(id, name)',
                                                           pageToken=page_token).execute()

                for file in response.get('files', []):
                    if file.get('name') == name:
                        return file.get('name')

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

        except HttpError as err:
            print(err)

    def make_new_auditFolder(self):
        if self.creds is None:
            self._oauth()
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)

        try:
            project_name = self.data["Project-Name"]
            print("project name:", project_name)

            folder_metadata = {
                'name': project_name,
                'parents': [self.AUDIT_FOLDER_ID],
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder_response = self.drive_service.files().create(body=folder_metadata).execute()
            self.new_auditFolder_id = folder_response.get('id')

            print("new folder id:", self.new_auditFolder_id)


        except HttpError as err:
            print(err)

    def make_new_auditDocs(self):
        if self.creds is None:
            self._oauth()
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)

        try:
            title = "[HEXAudit] DeFiContractAudit_"
            project_name = self.data["Project-Name"]
            title += project_name + "_v1.0_KR"
            body = {
                'name': title
            }
            drive_response = self.drive_service.files().copy(
                fileId=self.DOCUMENT_ID, body=body).execute()

            audit_docs_id = drive_response.get('id')
            audit_docs = self.drive_service.files().get(fileId=audit_docs_id,
                                                        fields='parents').execute()

            previous_parents_id = ",".join(audit_docs.get('parents'))

            audit_docs_id = self.drive_service.files().update(fileId=audit_docs_id,
                                                              addParents=self.new_auditFolder_id,
                                                              removeParents=previous_parents_id,
                                                              fields='id').execute()

            print("new audit docs id:", audit_docs_id)

        except HttpError as err:
            print(err)
