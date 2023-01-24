from json import JSONDecodeError
from typing import Optional
from meapi.credentials_managers.credentials_manager import CredentialsManager


class DjangoSessionCredentialsManager(CredentialsManager):
    """
    Django Session Credentials Manager
        - This class is used to store the credentials in a django session.

    Parameters:
        - session: (``django.contrib.sessions.backends.base.SessionBase``) The django session.
    """
    def __init__(self, session):
        super().__init__()
        self.session = session

    def get(self, phone_number: str) -> Optional[dict]:
        if not self.session.get(str(phone_number)):
            return None
        else:
            return self.session[str(phone_number)]

    def set(self, phone_number: str, data: dict):
        self.session[str(phone_number)] = data

    def update(self, phone_number: str, access_token: str):
        self.session[str(phone_number)]['access'] = access_token

    def delete(self, phone_number: str):
        if self.session.get(str(phone_number)):
            del self.session[str(phone_number)]
