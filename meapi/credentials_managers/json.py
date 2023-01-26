import json
import os
from json import JSONDecodeError
from typing import Optional, Dict
from meapi.credentials_managers import CredentialsManager


class JsonCredentialsManager(CredentialsManager):
    """
    Json Credentials Manager
        - This class is used to store the credentials in a json file/s.

    Parameters:
        - config_file: (``str``) The config json file path. *Default:* 'meapi_credentials.json'.
        - separate_files: (``bool``) If True, each phone number will have its own file: 'credentials_dir/phone_number.json'. *Default:* ``False``.
        - directory: (``str``) The directory where the credentials files will be stored. *Default:* ``meapi_credentials``.

    Raises:
        - FileExistsError: If the config file is not a valid json file.
    """
    def __init__(
        self,
        config_file: str = 'meapi_credentials.json',
        separate_files: bool = False,
        directory: str = 'meapi_credentials'
    ):
        super().__init__()
        self.config_file = config_file
        self._mode = 'single' if not separate_files else 'directory'
        self.directory = directory
        if self._mode == 'directory':
            try:
                os.mkdir(self.directory)
            except FileExistsError:
                pass
        if self._mode == 'single':
            if not os.path.exists(self.config_file):
                with open(self.config_file, "w") as new_config_file:
                    new_config_file.write('{}')
            else:
                try:
                    with open(self.config_file, "r") as config_file:
                        json.load(config_file)
                except JSONDecodeError:
                    raise FileExistsError("Not a valid json file: " + self.config_file)

    def get(self, phone_number: str) -> Optional[Dict[str, str]]:
        if self._mode == 'single':
            with open(self.config_file, "r") as config_file:
                try:
                    return json.load(config_file)[str(phone_number)]
                except KeyError:
                    return None
        else:
            try:
                with open(os.path.join(self.directory, phone_number + '.json'), "r") as config_file:
                    return json.load(config_file)
            except FileNotFoundError:
                return None

    def set(self, phone_number: str, data: Dict[str, str]):
        if self._mode == 'single':
            with open(self.config_file, "r") as config_file:
                existing_content = json.load(config_file)
            existing_content[phone_number] = data
            with open(self.config_file, "w") as config_file:
                json.dump(existing_content, config_file, indent=4)
        else:
            with open(os.path.join(self.directory, phone_number + '.json'), "w") as config_file:
                json.dump(data, config_file, indent=4)

    def update(self, phone_number: str, access_token: str):
        if self._mode == 'single':
            with open(self.config_file, "r") as config_file:
                existing_content = json.load(config_file)
            existing_content[phone_number]['access'] = access_token
            with open(self.config_file, "w") as config_file:
                json.dump(existing_content, config_file, indent=4)
        else:
            with open(os.path.join(self.directory, phone_number + '.json'), "r") as config_file:
                existing_content = json.load(config_file)
            existing_content['access'] = access_token
            with open(os.path.join(self.directory, phone_number + '.json'), "w") as config_file:
                json.dump(existing_content, config_file, indent=4)

    def delete(self, phone_number: str):
        if self._mode == 'single':
            with open(self.config_file, "r") as config_file:
                existing_content = json.load(config_file)
            del existing_content[phone_number]
            with open(self.config_file, "w") as config_file:
                json.dump(existing_content, config_file, indent=4)
        else:
            os.remove(os.path.join(self.directory, phone_number + '.json'))
