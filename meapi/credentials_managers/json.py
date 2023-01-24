import json
import os
from json import JSONDecodeError
from typing import Optional
from meapi.credentials_managers.credentials_manager import CredentialsManager


class JsonFileCredentialsManager(CredentialsManager):
    """
    Json File Credentials Manager
        - This class is used to store the credentials in a json file.

    Parameters:
        - config_file: (``str``) The config json file path. *Default:* 'config.json'.
    """
    def __init__(self, config_file: str = 'config.json'):
        super().__init__()
        if str(config_file).endswith(".json"):
            self.config_file = config_file
        else:
            raise ValueError("config_file must be a json file")

    def _read_or_create(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as config_file:
                try:
                    existing_content = json.load(config_file)
                except JSONDecodeError:
                    raise FileExistsError("Not a valid json file: " + self.config_file)
        else:
            with open(self.config_file, "w") as new_config_file:
                new_config_file.write('{}')
                existing_content = {}
        return existing_content

    def get(self, phone_number: str) -> Optional[dict]:
        existing_content = self._read_or_create()
        if not existing_content.get(str(phone_number)):
            return None
        else:
            return existing_content[str(phone_number)]

    def set(self, phone_number: str, data: dict):
        existing_content = self._read_or_create()
        existing_content[str(phone_number)] = data
        with open(self.config_file, "w") as config_file:
            json.dump(existing_content, config_file, indent=4, sort_keys=True)

    def update(self, phone_number: str, access_token: str):
        existing_content = self._read_or_create()
        existing_content[str(phone_number)]['access'] = access_token
        with open(self.config_file, "w") as config_file:
            json.dump(existing_content, config_file, indent=4, sort_keys=True)

    def delete(self, phone_number: str):
        existing_content = self._read_or_create()
        if existing_content.get(str(phone_number)):
            del existing_content[str(phone_number)]
            with open(self.config_file, "w") as config_file:
                json.dump(existing_content, config_file, indent=4, sort_keys=True)
