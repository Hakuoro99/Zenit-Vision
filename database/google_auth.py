import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleAuth:
    def __init__(self, secrets_file):
        self.secrets_file = secrets_file
        self.scopes = [
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid'
        ]

    def login(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, self.scopes)
            # Reducimos a 20 segundos para que sea más responsivo el error
            creds = flow.run_local_server(
                port=0, 
                prompt='select_account', 
                timeout_seconds=20, # <--- Importante
                open_browser=True
            )
            
            service = build('oauth2', 'v2', credentials=creds)
            return service.userinfo().get().execute()
        except Exception:
            return None # Si el usuario cierra o hay timeout, devuelve None