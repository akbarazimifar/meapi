from typing import Optional
from meapi.credentials_managers.credentials_manager import CredentialsManager


class MemoryCredentialsManager(CredentialsManager):
    """
    Memory Credentials Manager.
        - This class is used to store the credentials in memory.
    """
    def __init__(self):
        self.credentials = {}

    def get(self, phone_number: str) -> Optional[dict]:
        return self.credentials.get(str(phone_number))

    def set(self, phone_number: str, data: dict):
        self.credentials[str(phone_number)] = data

    def update(self, phone_number: str, access_token: str):
        self.credentials[str(phone_number)]['access'] = access_token

    def delete(self, phone_number: str):
        del self.credentials[str(phone_number)]
