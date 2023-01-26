from json import JSONDecodeError
from typing import Optional, Dict
from meapi.credentials_managers import CredentialsManager


class FlaskSessionCredentialsManager(CredentialsManager):
    """
    Flask Session Credentials Manager
        - This class is used to store the credentials in a flask session.

    Parameters:
        - session: (``flask.sessions.Session``) The flask session.
    """
    def __init__(self, session):
        super().__init__()
        self.session = session

    def get(self, phone_number: str) -> Optional[Dict[str, str]]:
        if not self.session.get(str(phone_number)):
            return None
        else:
            return self.session[str(phone_number)]

    def set(self, phone_number: str, data: Dict[str, str]):
        self.session[str(phone_number)] = data

    def update(self, phone_number: str, access_token: str):
        self.session[str(phone_number)]['access'] = access_token

    def delete(self, phone_number: str):
        if self.session.get(str(phone_number)):
            del self.session[str(phone_number)]